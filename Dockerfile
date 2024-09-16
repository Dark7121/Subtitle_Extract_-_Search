FROM python:3.12

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt /app/

RUN apt-get update \
    && apt-get install -y ffmpeg netcat-openbsd \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN chmod +x /app/wait-for-db.sh

EXPOSE 8000

CMD ["gunicorn", "mywebsite.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "600"]
