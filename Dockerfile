FROM python:3.12

RUN addgroup --gid 1000 appgroup \
    && adduser --disabled-password --gecos "" --uid 1000 --gid 1000 appuser

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN mkdir -p /app/uploads && chown -R 1000:1000 /app/uploads
RUN mkdir -p /app/logs && chown -R 1000:1000 /app/logs

USER appuser

CMD ["gunicorn", "app.app:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8080"]
