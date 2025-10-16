import os
from dotenv import find_dotenv, load_dotenv
from fastapi.templating import Jinja2Templates

# if not find_dotenv():
#     exit("Not exists .env")
# else:
#     load_dotenv()

templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "static", "templates")
)

DOMAIN = os.getenv("DOMAIN", None)
BOT_TOKEN = os.getenv("BOT_TOKEN", None)
CHAT_ID = os.getenv("CHAT_ID", None)

crypto_addresses = [
    {"currency": "BTC", "address": f"{os.getenv("BTC_ADDRESS")}"},
    {"currency": "ETH (ERC20)", "address": f"{os.getenv("ETH_ADDRESS")}"},
    {"currency": "SOL", "address": f"{os.getenv("SOL_ADDRESS")}"},
]
