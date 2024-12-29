from dotenv import load_dotenv, find_dotenv
import os
import logging
from aiogram import Bot, Dispatcher, F, types, Router
import sys
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(filename)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

if not find_dotenv():
    logging.error('.env is missing')
    exit("Переменные окружения не загружены т.к отсутствует файл .env (создайте по '.env.template')")
else:
    load_dotenv()

sys.stdout.reconfigure(encoding="utf-8")
disk_app_folder_name = '????????'
BOT_TOKEN = os.getenv('BOT_TOKEN')
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)
router = Router()
DEFAULT_COMMANDS = (
    ('start', "Старт / Перезапуск"),
    ('help', "Помогите")
)
