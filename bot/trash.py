# import asyncio
# import logging
# from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
#     KeyboardButton
# from aiogram.filters import Command
# from config import router, bot, dp, DEFAULT_COMMANDS
# from bot.handlers.default_handlers import start, echo, help
# from aiogram import Bot
# from aiogram.types import BotCommand
#
#
# # @dp.message()
# # async def log_message(message: Message):
# #     logging.info(f"Сообщение от {message.from_user.full_name}: {message.text}")
# #     await message.answer("Сообщение записано в лог!")
# #
# # # Подключаемся к базе данных
# # conn = sqlite3.connect("users.db")
# # cursor = conn.cursor()
# #
# # # Создаём таблицу пользователей
# # cursor.execute("""
# # CREATE TABLE IF NOT EXISTS users (
# #     id INTEGER PRIMARY KEY,
# #     name TEXT,
# #     username TEXT
# # )
# # """)
# # conn.commit()
# #
# # @dp.message(Command("register"))
# # async def register_user(message: Message):
# #     user_id = message.from_user.id
# #     name = message.from_user.full_name
# #     username = message.from_user.username
# #
# #     cursor.execute("INSERT OR IGNORE INTO users (id, name, username) VALUES (?, ?, ?)", (user_id, name, username))
# #     conn.commit()
# #     await message.answer("Вы успешно зарегистрированы!")
# #
# #
# # @dp.message(Command("photo"))
# # async def send_photo(message: Message):
# #     with open("example.jpg", "rb") as photo:
# #         await message.answer_photo(photo, caption="Это пример изображения!")
# #
# #
# # @dp.message(Command("file"))
# # async def send_file(message: Message):
# #     with open("example.pdf", "rb") as file:
# #         await message.answer_document(file, caption="Вот ваш файл!")
# #
# #
# # @dp.message(Command("pages"))
# # async def show_pages(message: Message):
# #     keyboard = InlineKeyboardMarkup(inline_keyboard=[
# #         [InlineKeyboardButton(text="Назад", callback_data="prev"),
# #          InlineKeyboardButton(text="Вперёд", callback_data="next")]
# #     ])
# #     await message.answer("Страница 1", reply_markup=keyboard)
# #
# #
# # @dp.callback_query()
# # async def handle_pagination(query: types.CallbackQuery):
# #     if query.data == "next":
# #         await query.message.edit_text("Страница 2", reply_markup=query.message.reply_markup)
# #     elif query.data == "prev":
# #         await query.message.edit_text("Страница 1", reply_markup=query.message.reply_markup)
# #     await query.answer()
# #
# #
# # @dp.message(F.content_type == "document")
# # async def handle_document(message: Message):
# #     await message.answer(f"Вы отправили документ: {message.document.file_name}")
# #
# #
# #
# # @router.message(Command("menu"))
# # async def show_menu(message: Message):
# #     """Handler for  /menu"""
# #     keyboard = InlineKeyboardMarkup(inline_keyboard=[
# #         [InlineKeyboardButton(text="Ссылка", url="https://example.com")],
# #         [InlineKeyboardButton(text="Кнопка 1", callback_data="btn1")],
# #         [InlineKeyboardButton(text="Кнопка 2", callback_data="btn2")]
# #     ])
# #     await message.answer("Выберите действие:", reply_markup=keyboard)
# #
# #
# # @router.callback_query()
# # async def handle_callback(query: CallbackQuery):
# #     """Хендлер для обработки callback-запросов"""
# #     if query.data == "btn1":
# #         await query.message.answer("Вы нажали Кнопка 1")
# #     elif query.data == "btn2":
# #         await query.message.answer("Вы нажали Кнопка 2")
# #     await query.answer()  # Подтверждаем обработку
# #
# #
# # @router.message(Command("options"))
# # async def show_options(message: Message):
# #     """Handler for /options"""
# #     keyboard = ReplyKeyboardMarkup(
# #         keyboard=[
# #             [KeyboardButton(text="Вариант 1"), KeyboardButton(text="Вариант 2")],
# #             [KeyboardButton(text="Отмена")]
# #         ],
# #         resize_keyboard=True
# #     )
# #     await message.answer("Выберите вариант:", reply_markup=keyboard)
#
# import yt_dlp
# import sys
# import subprocess
# import requests
# import os
# from dotenv import load_dotenv
# import json
# from loguru import logger
# import threading
# from Exeptions.exeptions_classes import DiskGetLinkError, PublishingFileError, FileDownloadError
# from config_data.config import uploads_path, disk_app_folder_name
# from handlers import error_handler
# from concurrent.futures import ThreadPoolExecutor
#
# load_dotenv()
# YA_TOKEN = os.getenv("YANDEX_DISK_TOKEN")
# COOKIES_FILE = "./cookies.txt"
#
#
# def get_video_name_from_uploads(id: str, format: str) -> str:
#     """Возвращает имя видеофайла из директории загрузок пользователя."""
#     logger.debug("youtube.get_video_name_from_uploads()")
#
#     uploads_user_dir = os.path.join(uploads_path, id)
#     for root, dirs, files in os.walk(uploads_user_dir):
#         for file in files:
#             if file.endswith(format):
#                 logger.debug(f"youtube.get_video_name_from_uploads() -> {file}")
#                 return file
#         raise FileNotFoundError
#
#
# def download_video(url, output_dir, cookies_file):
#     """Загружает видео с YouTube и сохраняет его в указанную директорию."""
#     logger.debug("youtube.download_video()")
#
#     output_template = os.path.join(output_dir, "%(title)s.%(ext)s")
#     command = [
#         "yt-dlp",
#         "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
#         "--merge-output-format", "mp4",
#         "-o", output_template,
#         "--write-info-json",
#         "--cookies", cookies_file,
#         url
#     ]
#     subprocess.run(command, check=True)
#     return True
#
#
# def upload_file_to_disk_folder(dir_path, file_name, disk_folder_path, ya_token):
#     """
#     Загружает файл на Яндекс.Диск в указанную директорию.
#
#     :param dir_path: Путь к локальной директории
#     :param file_name: Имя файла
#     :param disk_folder_path: Путь на Яндекс.Диске
#     :param ya_token: OAuth-токен для доступа к Яндекс.Диску
#     :raises: FileDownloadError, DiskGetLinkError
#     :return: True, если файл успешно загружен
#     """
#     logger.debug("youtube.upload_file_to_disk_folder()")
#     url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
#     headers = {"Authorization": f"OAuth {ya_token}"}
#     params = {"path": f"{disk_folder_path}/{file_name}", "overwrite": "true"}
#
#     try:
#         logger.debug("Выполняю запрос на диск для получения ссылки")
#         response = requests.get(url, headers=headers, params=params)
#         response.raise_for_status()  # Выбросить исключение, если код не 2xx
#
#         upload_url = response.json().get("href")
#         if not upload_url:
#             logger.error("Не удалось получить ссылку для загрузки")
#             raise DiskGetLinkError("Не удалось получить ссылку для загрузки")
#     except requests.RequestException as e:
#         logger.error(f"Ошибка при получении ссылки: {e}")
#         raise DiskGetLinkError(f"Ошибка при получении ссылки: {e}")
#
#     path = os.path.join(dir_path, file_name)
#     logger.debug(f"Путь к файлу: {path}")
#
#     if not os.path.isfile(path):
#         logger.error(f"Файл не найден: {path}")
#         raise FileNotFoundError(f"Файл не найден: {path}")
#
#     def upload_file():
#         """Выполняет загрузку файла в отдельном потоке."""
#         with open(path, "rb") as f:
#             try:
#                 logger.debug("Начинаю загрузку файла на Яндекс.Диск")
#                 upload_response = requests.put(upload_url, files={"file": f})
#                 upload_response.raise_for_status()  # Проверить успешность запроса
#                 return upload_response.status_code
#             except requests.RequestException as e:
#                 logger.error(f"Ошибка при загрузке файла: {e}")
#                 raise FileDownloadError(f"Ошибка при загрузке файла: {e}")
#
#     # Выполняем загрузку в отдельном потоке
#     with ThreadPoolExecutor(max_workers=1) as executor:
#         future = executor.submit(upload_file)
#         try:
#             status_code = future.result()  # Ждём завершения потока
#             if status_code == 201:
#                 logger.debug("Файл успешно загружен")
#                 return True
#             else:
#                 logger.error(f"Ошибка загрузки: статус {status_code}")
#                 raise FileDownloadError(f"Ошибка загрузки: статус {status_code}")
#         except FileDownloadError as e:
#             logger.error(f"Ошибка в процессе загрузки: {e}")
#             raise
#
#
# def get_file_shareable_link(file_path):
#     """Публикует файл на Яндекс.Диске и возвращает публичную ссылку."""
#     logger.debug("youtube.get_file_shareable_link()")
#
#     url_publish = "https://cloud-api.yandex.net/v1/disk/resources/publish"
#     headers = {"Authorization": f"OAuth {YA_TOKEN}"}
#     params = {"path": file_path}
#
#     response = requests.put(url_publish, headers=headers, params=params)
#     if response.status_code == 200:
#         url_meta = "https://cloud-api.yandex.net/v1/disk/resources"
#         response_meta = requests.get(url_meta, headers=headers, params=params)
#         if response_meta.status_code == 200:
#             share_url = response_meta.json().get("public_url")
#             return share_url
#         else:
#             raise DiskGetLinkError
#     else:
#         raise PublishingFileError
#
#
# def main(user_upl_path, link: str):
#     """Основная функция для загрузки и обработки видео."""
#     logger.debug("youtube.main()")
#
#     download_video(link, user_upl_path, COOKIES_FILE)
#     video_name = get_video_name_from_uploads(user_upl_path, "mp4")
#
#     yandex_disk_file_path = f"disk:/Приложения/{disk_app_folder_name}/{video_name}"
#     upload_file_to_disk_folder(user_upl_path, video_name, "disk:/Приложения/bot_convert")
#
#     share_url = get_file_shareable_link, yandex_disk_file_path
#     return share_url
