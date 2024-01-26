FROM python:3.9-slim
COPY . /searchengine

WORKDIR /searchengine
RUN apt-get update && apt-get install -y build-essential

RUN pip install --upgrade pip && pip install -r requirements.txt


EXPOSE 8080

CMD ["python","app.py"]