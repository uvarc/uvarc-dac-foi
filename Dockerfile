FROM python:3.12-slim

WORKDIR /app

COPY backend /app/backend
COPY frontend /app/frontend

RUN pip install --no-cache-dir -r /app/backend/requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.app:app"]