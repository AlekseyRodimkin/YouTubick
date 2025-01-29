from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import aiohttp

from bot.states.states import UserState
from bot.config import API

youtube_router = Router()


@youtube_router.message(UserState.waiting_youtube_link)
async def process_youtube_link(message: Message, state: FSMContext):
    """YouTube link handler"""
    youtube_link = message.text

    if True:  # todo link checker
        api_url = f"{API}/download"
        payload = {"url": youtube_link}
        headers = {"Authorization": "Bearer YOUR_API_KEY"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(api_url, data=payload, headers=headers) as response:
                    response.raise_for_status()

                    if response.status == 200:
                        await message.answer(f"🤖✅ Ссылка принята: {youtube_link}\nСкачиваю видео.")
                    else:
                        await message.answer(f"🤖🚫 Ошибка при скачивании видео: {await response.text()}")
        except aiohttp.ClientError as e:
            await message.answer(f"🤖🚫 Ошибка при отправке запроса: {str(e)}")

        await state.clear()
    else:
        await message.answer("🤖🚫 Это не похоже на ссылку YouTube. Попробуйте снова.")
