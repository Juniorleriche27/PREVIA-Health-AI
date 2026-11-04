"""PREVIA provider-neutral LLM gateway.

Only locally registered adapters/endpoints can receive questions.  Client input is
restricted to registered provider IDs and model names; API keys never cross the API.
No provider is selected or contacted automatically.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any
from urllib.parse import quote, urlsplit

import httpx

MODULE_ROOT = Path(__file__).resolve().parents[1]
ADAPTERS = {"openai_compatible", "anthropic", "gemini", "cohere", "knowlia"}
ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{1,40}$")
MODEL_PATTERN = re.compile(r"^[\w./:@+\-]{1,160}$", re.ASCII)


class ProviderError(Exception):
    """A registered provider could not deliver a safe, usable response."""


def config_path() -> Path:
    return Path(os.getenv("PREVIA_LLM_CONFIG_FILE", "")).expanduser() if os.getenv("PREVIA_LLM_CONFIG_FILE") else MODULE_ROOT / "config" / "providers.local.json"


def _check_endpoint(url: str) -> str:
    p = urlsplit(url)
    # User-owned configuration only. Avoid forwarding credentials to arbitrary
    # insecure remote HTTP hosts. Local servers may use HTTP explicitly.
    if p.username or p.password or p.query or p.fragment or not p.hostname:
        raise ValueError("Endpoint mal formé.")
    local = p.hostname in {"127.0.0.1", "localhost", "::1"}
    if p.scheme != "https" and not (local and p.scheme == "http"):
        raise ValueError("HTTPS est requis hors de localhost.")
    return url.rstrip("/")


def _check_knowlia_endpoint(url: str) -> str:
    """Allow HTTPS or the fixed Docker service names on a private network."""
    p = urlsplit(url)
    if p.username or p.password or p.query or p.fragment or not p.hostname:
        raise ValueError("Endpoint Knowlia mal formé.")
    internal = p.hostname in {"prod_knowlia", "knowlia"}
    if p.scheme != "https" and not (internal and p.scheme == "http"):
        raise ValueError("HTTPS est requis hors du réseau Docker Knowlia.")
    return url.rstrip("/")


def _configs() -> list[dict[str, Any]]:
    file = config_path()
    if not file.is_file():
        return []
    try:
        data = json.loads(file.read_text(encoding="utf-8-sig"))
        entries = data["providers"]
        if not isinstance(entries, list) or len(entries) > 32:
            raise ValueError("Liste de fournisseurs invalide.")
        ids: set[str] = set()
        for p in entries:
            if not isinstance(p, dict) or not ID_PATTERN.fullmatch(p.get("id", "")):
                raise ValueError("Identifiant de fournisseur invalide.")
            if p["id"] in ids or p.get("adapter") not in ADAPTERS:
                raise ValueError("Fournisseur dupliqué ou adaptateur inconnu.")
            ids.add(p["id"])
            if not isinstance(p.get("default_model"), str) or not MODEL_PATTERN.fullmatch(p["default_model"]):
                raise ValueError("Modèle configuré invalide.")
            if p["adapter"] == "openai_compatible":
                _check_endpoint(p.get("base_url", ""))
            if p["adapter"] == "knowlia":
                _check_knowlia_endpoint(p.get("base_url", ""))
                tenant_id = p.get("tenant_id", "previa-health-ai")
                if not isinstance(tenant_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{2,79}", tenant_id):
                    raise ValueError("Tenant Knowlia invalide.")
            if "api_key_env" in p and (not isinstance(p["api_key_env"], str) or not re.fullmatch(r"[A-Z][A-Z0-9_]{2,100}", p["api_key_env"])):
                raise ValueError("Variable de clé API invalide.")
            timeout = p.get("timeout_seconds", 25)
            if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not 2 <= timeout <= 60:
                raise ValueError("Délai fournisseur invalide (2 à 60 secondes).")
            max_tokens = p.get("max_tokens", 350)
            if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or not 64 <= max_tokens <= 1200:
                raise ValueError("Limite de sortie fournisseur invalide (64 à 1200 jetons).")
        return entries
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise ProviderError("Configuration multi-fournisseurs invalide.") from exc


def providers_public() -> list[dict[str, Any]]:
    result = []
    for p in _configs():
        if not p.get("enabled", True):
            continue
        key_name = p.get("api_key_env", "")
        configured = bool(os.getenv(key_name)) if key_name else p["adapter"] == "openai_compatible" and urlsplit(p.get("base_url", "")).hostname in {"127.0.0.1", "localhost", "::1"}
        result.append({"id": p["id"], "label": p.get("label", p["id"]), "adapter": p["adapter"], "default_model": p["default_model"], "ready": configured})
    return result


def _response_text(payload: dict[str, Any], adapter: str) -> str:
    if adapter == "openai_compatible":
        content = payload["choices"][0]["message"]["content"]
        if isinstance(content, str):
            return content
        return "\n".join(item["text"] for item in content if item.get("type") == "text")
    if adapter == "anthropic":
        return "\n".join(c["text"] for c in payload["content"] if c.get("type") == "text")
    if adapter == "gemini":
        return "\n".join(c["text"] for c in payload["candidates"][0]["content"]["parts"] if "text" in c)
    if adapter == "cohere":
        return "\n".join(c["text"] for c in payload["message"]["content"] if c.get("type") == "text")
    if adapter == "knowlia":
        return payload["data"]["content"]
    raise ProviderError("Type de réponse non pris en charge.")


def generate(provider_id: str, model_id: str | None, system_prompt: str, user_prompt: str, history: list[dict[str, str]] | None = None) -> tuple[str, str]:
    """Generate via an explicitly requested, locally configured provider.

    Returns (generated_text, effective_model_name). This function never picks a
    vendor automatically, never cascades to another vendor and never logs keys.
    """
    configs = [p for p in _configs() if p["id"] == provider_id and p.get("enabled", True)]
    if not configs:
        raise ProviderError("Fournisseur demandé absent de la configuration locale.")
    p = configs[0]
    model = (model_id or p["default_model"]).strip()
    if not MODEL_PATTERN.fullmatch(model):
        raise ProviderError("Identifiant de modèle invalide.")
    key_env = p.get("api_key_env", "")
    key = os.getenv(key_env, "") if key_env else ""
    if key_env and not key:
        raise ProviderError("Clé API de ce fournisseur non configurée.")
    messages = [{"role": "system", "content": system_prompt}]
    for turn in (history or [])[-6:]:
        if turn.get("role") in {"user", "assistant"} and isinstance(turn.get("content"), str):
            messages.append({"role": turn["role"], "content": turn["content"][:700]})
    messages.append({"role": "user", "content": user_prompt})
    adapter = p["adapter"]
    max_tokens = p.get("max_tokens", 350)
    if adapter == "openai_compatible":
        url = _check_endpoint(p["base_url"]) + "/chat/completions"
        headers = {"Authorization": f"Bearer {key}"} if key else {}
        body = {"model": model, "messages": messages, "stream": False, "max_tokens": max_tokens, "temperature": 0.1}
    elif adapter == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {"x-api-key": key, "anthropic-version": "2023-06-01"}
        body = {"model": model, "system": system_prompt, "max_tokens": max_tokens, "temperature": 0.1, "messages": messages[1:]}
    elif adapter == "gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{quote(model, safe='')}:generateContent"
        headers = {"x-goog-api-key": key}
        body = {"systemInstruction": {"parts": [{"text": system_prompt}]}, "contents": [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]} for m in messages[1:]], "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.1}}
    elif adapter == "cohere":
        url = "https://api.cohere.com/v2/chat"
        headers = {"Authorization": f"Bearer {key}"}
        body = {"model": model, "messages": messages, "stream": False, "max_tokens": max_tokens, "temperature": 0.1}
    elif adapter == "knowlia":
        url = _check_knowlia_endpoint(p["base_url"]) + "/public/v1/generate"
        headers = {"X-Knowlia-Api-Key": key}
        body = {
            "tenant_id": p.get("tenant_id", "previa-health-ai"),
            "messages": messages,
            "model": model,
            "temperature": 0.1,
            "max_tokens": max_tokens,
            "timeout_seconds": p.get("timeout_seconds", 25),
            "web_access": "off",
            "metadata": {"application": "previa-health-ai", "mode": "grounded-rag"},
        }
    else:
        raise ProviderError("Adaptateur non disponible.")
    try:
        timeout = httpx.Timeout(float(p.get("timeout_seconds", 25)), connect=min(10.0, float(p.get("timeout_seconds", 25))))
        with httpx.Client(timeout=timeout, follow_redirects=False) as client:
            response = client.post(url, headers=headers, json=body)
            response.raise_for_status()
            payload = response.json()
            result = _response_text(payload, adapter).strip()
            if adapter == "knowlia":
                model = payload.get("data", {}).get("model", model)
        if not result or len(result) > 12000:
            raise ProviderError("Réponse vide ou excessive du fournisseur.")
        return result[:3000], model
    except (httpx.HTTPError, ValueError, TypeError, KeyError, IndexError) as exc:
        # Internal HTTP errors and API keys must not be returned to the browser.
        raise ProviderError("Fournisseur momentanément indisponible ou réponse non compatible.") from exc
