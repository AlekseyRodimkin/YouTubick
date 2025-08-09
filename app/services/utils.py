import os
import smtplib
import time
import uuid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import parse_qs, urlparse

import aiohttp
import redis
from yt_dlp import YoutubeDL

from config import SMTP_PASSWORD, SMTP_SERVER, SMTP_USER, logger, REDIS_HOST, REDIS_PORT

app_logger = logger.bind(name="app")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


def send_mail(subject, body, to_email):
    smtp_port = 587

    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, smtp_port)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()

        app_logger.info("✅ Письмо успешно отправлено.")
    except Exception as e:
        app_logger.warning("❌ Ошибка при отправке письма:", e)


async def get_stream_url(url: str) -> str | None:
    """Получает прямую ссылку на видео через yt-dlp"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": False,
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "extract_flat": False,
        "socket_timeout": 15,
        "ignoreerrors": True,
        "geo_bypass": True,
        "age_limit": 18,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "skip": ["dash", "hls"]
            }
        },
        "allow_multiple_video_streams": True,
        "allow_multiple_audio_streams": True,
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get("url") if info else None


async def fetch_video_metadata(stream_url: str):
    """Получает размер видео и поддерживает ли он докачку"""
    async with aiohttp.ClientSession() as session:
        async with session.head(stream_url) as resp:
            accept_ranges = resp.headers.get("Accept-Ranges", "none")
            content_length = int(resp.headers.get("Content-Length", 0))
            return content_length, accept_ranges == "bytes"


def generate_unique_string(prefix: str = "") -> str:
    """Генерирует уникальную строку с опциональным префиксом"""
    unique_str = f"{prefix}{uuid.uuid4().hex}_{int(time.time() * 1000)}"
    return unique_str


async def is_valid_youtube_url(url: str) -> bool:
    """Проверяет, является ли youtube ссылка валидной"""
    result = urlparse(url)

    if not all([result.scheme in ("http", "https"), result.netloc]):
        return False

    if not any(domain in result.netloc for domain in ["youtube.com", "youtu.be"]):
        return False

    if "youtube.com" in result.netloc:
        if "watch" in result.path:
            query = parse_qs(result.query)
            return "v" in query and len(query["v"][0]) == 11

        elif "/v/" in result.path:
            video_id = result.path.split("/v/")[1]
            return len(video_id) == 11

    elif "youtu.be" in result.netloc:
        video_id = result.path[1:]
        return len(video_id) == 11

    elif "embed" in result.path:
        video_id = result.path.split("/")[-1]
        return len(video_id) == 11

    return False


def file_streamer(file_path: str, chunk_size: int = 1024 * 1024):
    """Передает файл, удаляет по завершению"""
    try:
        with open(file_path, "rb") as f:
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


async def stream_generator(start, end, supports_range, stream_url):
    timeout = aiohttp.ClientTimeout(total=3600)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept": "*/*",
        "Referer": "https://www.youtube.com/",
    }

    if supports_range:
        headers["Range"] = f"bytes={start}-{end}"

    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(stream_url, headers=headers) as resp:
                if resp.status not in (200, 206):
                    raise aiohttp.ClientError(f"Invalid response status: {resp.status}")

                async for chunk in resp.content.iter_chunked(1024 * 8):
                    yield chunk
        except aiohttp.ClientConnectionError as e:
            app_logger.error(f"[stream_generator] Connection error: {e}")
            return


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
