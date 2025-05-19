import os
from dotenv import find_dotenv, load_dotenv

from celery import Celery
from fastapi.templating import Jinja2Templates

if not find_dotenv():
    exit("Not exists .env")
else:
    load_dotenv()

# templates = Jinja2Templates(directory="/home/aleksei/PycharmProjects/youtube_video/app/static/templates")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", None)
SMTP_SERVER = os.getenv("SMTP_SERVER", None)
SMTP_PORT = os.getenv("SMTP_PORT", None)
SMTP_USER = os.getenv("SMTP_USER", None)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", None)
EMAIL_PASS_FOR_TEST_ENDPOINT = os.getenv("EMAIL_PASS_FOR_TEST_ENDPOINT", None)

celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:6379/0",
    backend=f"redis://{REDIS_HOST}:6379/0",
    include=["app.services.tasks"]
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
)

crypto_addresses = [
    {
        "currency": "BTC",
        "address": f"{os.getenv("BTC_ADDRESS")}"
    },
    {
        "currency": "ETH",
        "address": f"{os.getenv("ETH_ADDRESS")}"
    },
    {
        "currency": "SOL",
        "address": f"{os.getenv("SOL_ADDRESS")}"
    },
]
