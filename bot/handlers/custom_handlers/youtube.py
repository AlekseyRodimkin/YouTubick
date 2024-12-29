from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

youtube_router = Router()


@youtube_router.message(Command("youtube"))
async def cmd_youtube(message: Message):
    """Handler for /youtube"""
    await message.answer(f"🤖youtube")
