FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY . .

CMD ["gunicorn", "app.app:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4", "-b", "0.0.0.0:8000"]
