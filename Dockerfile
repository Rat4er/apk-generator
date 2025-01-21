#Да это ебанешься какие костыли, но это самый просто и быстрый вариант
FROM openjdk:11-jdk-slim

#Вообще ебнулся, ставит питон в имедже жабы (´。＿。｀)
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 5000

#без комментариев
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
