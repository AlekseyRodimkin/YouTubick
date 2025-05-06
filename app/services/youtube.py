import yt_dlp
import os
from config.logging_config import logger
import uuid
import time

app_logger = logger.bind(name="app")


async def generate_unique_string(prefix: str = "") -> str:
    """Генерирует уникальную строку с опциональным префиксом"""
    unique_str = f"{prefix}{uuid.uuid4().hex}_{int(time.time() * 1000)}"
    return unique_str


async def download_video(url, output_dir='uploads') -> str:
    """Скачивает видео и возвращает имя файла"""
    try:
        app_logger.info(f"download_video({url})")

        name = await generate_unique_string("your_video__")
        output_template = os.path.join(output_dir, f"{name}.%(ext)s")

        ydl_opts = {
            'format': 'bestvideo[vcodec^=avc1]+bestaudio/best[vcodec^=avc1]',
            'merge_output_format': 'mp4',
            'outtmpl': output_template,
            'noplaylist': True,
            'postprocessor_args': ['-movflags', '+faststart'],
            'quiet': False,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp4'

            if os.path.exists(filename):
                app_logger.debug(f"Видео сохранено: {url}")
                return filename
    except Exception as e:
        app_logger.exception(f"Download error: {e}")
        raise Exception(f"Download error: {e}")
