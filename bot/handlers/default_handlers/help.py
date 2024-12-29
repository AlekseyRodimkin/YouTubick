from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

help_router = Router()

@help_router.message(Command("help"))
async def cmd_help(message: Message):
    """Handler for /help"""
    await message.answer("🤖 Я могу выполнить следующие команды:\n/start - Запуск\n/help - Помощь")
