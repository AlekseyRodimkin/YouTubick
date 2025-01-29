from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from bot.config import services
from bot.states.states import UserState

start_router = Router()


@start_router.callback_query(lambda c: c.data.startswith("service_"))
async def process_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    service_name = callback.data.split("_", 1)[1]

    if service_name in services:
        await state.set_state(UserState.waiting_youtube_link)
        await callback.message.answer(
            f"🤖 Выбран сервис <b>{service_name}</b>.\nПришлите ссылку на видео",
            parse_mode="HTML"
        )
    else:
        await callback.message.answer("🤖 Ошибка выбора")

    await callback.answer()


@start_router.message(Command("start"))
async def cmd_start(message: Message):
    """Handler /start command"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=service, callback_data=f"service_{service}")]
            for service in services
        ]
    )
    await message.answer(
        f"🤖 Приветствую, {message.from_user.first_name}!\nВыберите сервис для работы:",
        reply_markup=keyboard
    )
