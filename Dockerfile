FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p logs
RUN mkdir -p data

VOLUME ["/app/data"]

ENTRYPOINT ["python", "main.py"]

CMD []
