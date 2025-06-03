import uvicorn

from app.app import app

app = app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
    # celery -A config.config worker --loglevel=info
