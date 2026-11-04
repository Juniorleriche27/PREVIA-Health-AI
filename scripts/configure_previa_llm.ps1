param(
    [Parameter(Position=0)][ValidateSet('add','list','remove')][string]$Action='list',
    [string]$Id,
    [ValidateSet('openai_compatible','anthropic','gemini','cohere')][string]$Adapter='openai_compatible',
    [string]$Model,
    [string]$BaseUrl,
    [string]$Label,
    [switch]$NoApiKey
)
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
$dir=Join-Path $root 'PREVIA_AI_XAI_RAG\config'
New-Item -ItemType Directory -Path $dir -Force | Out-Null
$file=Join-Path $dir 'providers.local.json'
$secretFile=Join-Path $dir 'secrets.dpapi.json'
$utf8=New-Object System.Text.UTF8Encoding($false)
$providers=@()
if(Test-Path $file) {
    $loaded=Get-Content -LiteralPath $file -Raw -Encoding UTF8 | ConvertFrom-Json
    $providers=@($loaded.providers)
}
$secretStore=@{}
if(Test-Path $secretFile) {
    $loaded=Get-Content -LiteralPath $secretFile -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach($property in $loaded.PSObject.Properties) { $secretStore[$property.Name]=$property.Value }
}
if($Action -eq 'list') {
    if($providers.Count -eq 0){ Write-Host 'Aucun fournisseur configure. Mode documentaire actif.'; exit 0 }
    $providers | Select-Object id,label,adapter,default_model,enabled | Format-Table -AutoSize
    exit 0
}
if($Id -notmatch '^[a-z][a-z0-9_-]{1,40}$'){ throw 'Id requis : lettres minuscules, chiffres, _ ou - (2 a 41 caracteres).' }
if($Action -eq 'remove') {
    $providers=@($providers | Where-Object { $_.id -ne $Id })
    $secretStore.Remove($Id)
} else {
    if([string]::IsNullOrWhiteSpace($Model)) { throw 'Preciser -Model avec un identifiant de modele.' }
    if($Model -notmatch '^[a-zA-Z0-9_./:@+\-]{1,160}$') { throw 'Identifiant de modele invalide.' }
    if($Adapter -eq 'openai_compatible') {
        if([string]::IsNullOrWhiteSpace($BaseUrl)){ throw 'Preciser -BaseUrl pour une API compatible OpenAI.' }
        $uri=$null
        if(-not [uri]::TryCreate($BaseUrl,[UriKind]::Absolute,[ref]$uri)) { throw 'BaseUrl invalide.' }
        $local=$uri.Host -in @('localhost','127.0.0.1','::1')
        if($uri.Scheme -ne 'https' -and -not ($uri.Scheme -eq 'http' -and $local)) {
            throw 'HTTPS requis sauf pour localhost.'
        }
    }
    $keyVariable='PREVIA_LLM_KEY_' + (($Id.ToUpperInvariant()) -replace '[^A-Z0-9]', '_')
    $entry=@{id=$Id;label= $(if($Label){$Label}else{$Id});adapter=$Adapter;default_model=$Model;enabled=$true;api_key_env=$keyVariable}
    if($Adapter -eq 'openai_compatible'){$entry.base_url=$BaseUrl.TrimEnd('/')}
    $providers=@($providers | Where-Object { $_.id -ne $Id }) + @($entry)
    if(-not $NoApiKey){
        $secret=Read-Host -Prompt "Cle API pour $Id (saisie masquee, chiffree par Windows DPAPI)" -AsSecureString
        if($secret.Length -eq 0){throw 'Cle vide. Utiliser -NoApiKey uniquement pour un modele local.'}
        $secretStore[$Id]=ConvertFrom-SecureString -SecureString $secret
    } elseif($Adapter -ne 'openai_compatible' -or $BaseUrl -notmatch '^http://(127\.0\.0\.1|localhost)(:\d+)?/') {
        throw '-NoApiKey est reserve aux endpoints localhost compatibles OpenAI.'
    } else {
        $entry.Remove('api_key_env')
        $secretStore.Remove($Id)
    }
}
[System.IO.File]::WriteAllText($file,(@{providers=@($providers)}|ConvertTo-Json -Depth 8),$utf8)
[System.IO.File]::WriteAllText($secretFile,($secretStore|ConvertTo-Json -Depth 5),$utf8)
Write-Host "Configuration enregistree pour $Id. Redemarrer: .\scripts\previa_full.ps1 restart" -ForegroundColor Green
