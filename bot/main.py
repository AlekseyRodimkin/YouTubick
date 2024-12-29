import asyncio
import logging
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton
from aiogram.filters import Command
from config import router, bot, dp, DEFAULT_COMMANDS
from bot.handlers.default_handlers import start, echo, help
from bot.handlers.custom_handlers import youtube
from aiogram import Bot
from aiogram.types import BotCommand


async def set_default_commands():
    """Set default commands"""
    commands = [BotCommand(command=command, description=description) for command, description in DEFAULT_COMMANDS]
    await bot.set_my_commands(commands)


async def main():
    logging.info("----- Bot started -----")

    # set default commands
    await set_default_commands()

    # connect routes
    dp.include_router(router)
    dp.include_router(start.start_router)
    dp.include_router(help.help_router)
    dp.include_router(echo.echo_router)
    dp.include_router(youtube.youtube_router)

    # start
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
