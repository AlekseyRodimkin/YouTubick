from aiogram.types import Message
from aiogram import Router

echo_router = Router()

# @echo_router.message()
# async def echo_handler(message: Message):
#     """Handler for echo"""
#     await message.answer(
#         text="🤖 Я тебя не понимаю.\nНажми /start или /help",
#         reply_to_message_id=message.message_id
#     )
