# Use the official Python slim image
FROM python:3.10-slim

WORKDIR /app

# Copy backend files
COPY backend ./backend

WORKDIR /app/backend

RUN apt-get update && apt-get install -y git build-essential && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
