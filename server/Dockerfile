FROM openjdk:11-jdk-slim

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY /server /app/server
COPY /apk_data /app/apk_data
COPY /apk_data_v2 /app/apk_data_v2
COPY /apk_worker /app/apk_worker
COPY /utils /app/utils
COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "600", "server.app:app"]
