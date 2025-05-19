import os
import uuid
import time
import aiohttp
import redis

from urllib.parse import urlparse, parse_qs
from yt_dlp import YoutubeDL

from config.logging_config import logger
from config.config import templates

app_logger = logger.bind(name="app")
r = redis.Redis()


async def get_stream_url(url: str) -> str | None:
    """Получает прямую ссылку на видео через yt-dlp"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "format": "best",
        "extract_flat": False,
        "socket_timeout": 10
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('url') if info else None


async def fetch_video_metadata(stream_url: str):
    """Получает размер видео и поддерживает ли он докачку"""
    async with aiohttp.ClientSession() as session:
        async with session.head(stream_url) as resp:
            accept_ranges = resp.headers.get('Accept-Ranges', 'none')
            content_length = int(resp.headers.get('Content-Length', 0))
            return content_length, accept_ranges == 'bytes'


def generate_unique_string(prefix: str = "") -> str:
    """Генерирует уникальную строку с опциональным префиксом"""
    unique_str = f"{prefix}{uuid.uuid4().hex}_{int(time.time() * 1000)}"
    return unique_str


async def is_valid_youtube_url(url: str) -> bool:
    """Проверяет, является ли youtube ссылка валидной"""
    app_logger.info(f"is_valid_youtube_url({url})")
    result = urlparse(url)

    if not all([result.scheme in ('http', 'https'), result.netloc]):
        return False

    if not any(domain in result.netloc for domain in ['youtube.com', 'youtu.be']):
        return False

    if 'youtube.com' in result.netloc:
        if 'watch' in result.path:
            query = parse_qs(result.query)
            return 'v' in query and len(query['v'][0]) == 11

        elif '/v/' in result.path:
            video_id = result.path.split('/v/')[1]
            return len(video_id) == 11

    elif 'youtu.be' in result.netloc:
        video_id = result.path[1:]
        return len(video_id) == 11

    elif 'embed' in result.path:
        video_id = result.path.split('/')[-1]
        return len(video_id) == 11

    return False


def file_streamer(file_path: str, chunk_size: int = 1024 * 1024):
    """Передает файл, удаляет по завершению"""
    try:
        app_logger.info(f"file_streamer({file_path})")

        with open(file_path, 'rb') as f:
            while chunk := f.read(chunk_size):
                yield chunk
    finally:
        os.remove(file_path)
        filename = os.path.basename(file_path)
        if "__" in filename:
            _, tail = filename.split("__", 1)
            video_id, *_ = tail.split(".", 1)
            key = f"video:{video_id}"
            r.delete(key)
            app_logger.info(f"Redis key {key} удалён")


async def return_index_page(request=None,
                            title="Главная страница",
                            message=None,
                            video_url=None):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": title,
            "messages": [{"status": message[0], "text": message[1]} if message else []],
            "video_url": video_url
        }
    )


async def return_error_page(request=None,
                            title="Ошибка",
                            message=None):
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "title": title,
            "messages": [{"code": message[0], "text": message[1]} if message else []]
        }
    )


def extract_video_id(url: str) -> str | None:
    parsed_url = urlparse(url)

    # https://www.youtube.com/watch?v=VIDEO_ID
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        query = parse_qs(parsed_url.query)
        return query.get("v", [None])[0]

    # https://youtu.be/VIDEO_ID
    if parsed_url.hostname in ["youtu.be"]:
        return parsed_url.path.lstrip("/")

    return None
