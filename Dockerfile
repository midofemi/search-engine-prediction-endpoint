# Stage 1: Build dependencies
FROM python:3.9-slim as builder

RUN apt-get update && apt-get install -y build-essential

WORKDIR /searchengine

COPY Search_Engine/search-engine-prediction-endpoint/requirements.txt .

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-slim

WORKDIR /searchengine

COPY --from=builder /searchengine/.venv /searchengine/.venv
COPY . .

ENV PATH="/searchengine/.venv/bin:$PATH"

EXPOSE 8080

CMD ["python", "app.py"]
