from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

start_router = Router()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Handler for /start"""
    await message.answer(f"🤖Приветствую, {message.from_user.first_name}")
