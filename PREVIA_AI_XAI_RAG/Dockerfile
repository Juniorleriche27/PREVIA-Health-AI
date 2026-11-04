FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PREVIA_PROJECT_ROOT=/app
WORKDIR /app
COPY PREVIA_AI_XAI_RAG/requirements-ai.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY PREVIA_AI_XAI_RAG/ai_service ./ai_service
COPY PREVIA_AI_XAI_RAG/knowledge ./knowledge
COPY PREVIA_AI_XAI_RAG/config ./config
COPY PREVIA_ML_Validation_Externe/results/cross_cycle /models/cross_cycle
RUN mkdir -p /app/PREVIA_ML_Validation_Externe/results && ln -s /models/cross_cycle /app/PREVIA_ML_Validation_Externe/results/cross_cycle
USER 65532:65532
EXPOSE 8766
CMD ["uvicorn", "ai_service.app:app", "--host", "0.0.0.0", "--port", "8766", "--no-access-log"]
