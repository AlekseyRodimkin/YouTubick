import os

from celery import Celery
from dotenv import find_dotenv, load_dotenv
from fastapi.templating import Jinja2Templates

# if not find_dotenv():
#     exit("Not exists .env")
# else:
#     load_dotenv()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static", "templates")
)
uploads_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
SMTP_SERVER = os.getenv("SMTP_SERVER", None)
SMTP_PORT = os.getenv("SMTP_PORT", None)
SMTP_USER = os.getenv("SMTP_USER", None)
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", None)
DOMAIN = os.getenv("DOMAIN", None)

celery_app = Celery(
    "tasks",
    broker=f"redis://{REDIS_HOST}:6379/0",
    backend=f"redis://{REDIS_HOST}:6379/0",
    include=["app.services.tasks"],
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
)

crypto_addresses = [
    {"currency": "BTC", "address": f"{os.getenv("BTC_ADDRESS")}"},
    {"currency": "ETH (ERC20)", "address": f"{os.getenv("ETH_ADDRESS")}"},
    {"currency": "SOL", "address": f"{os.getenv("SOL_ADDRESS")}"},
]
