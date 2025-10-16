import aiohttp
from urllib.parse import parse_qs, urlparse
from yt_dlp import YoutubeDL

from ..config import BOT_TOKEN, CHAT_ID


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


async def send_bot_notif():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": "Новый запрос"}

    async with aiohttp.ClientSession() as session:
        await session.post(url, data=payload)
