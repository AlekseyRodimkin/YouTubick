import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.services import (
    exception_handler,
    fetch_video_metadata,
    get_stream_url,
    stream_generator,
)

live_router = APIRouter()
app_logger = logging.getLogger(__name__)


@live_router.get("/live_play", status_code=200, response_class=JSONResponse)
@exception_handler()
async def get_live_play_url(request: Request, url: str) -> JSONResponse:
    """Возвращает JSON с URL для стриминга видео."""
    app_logger.info(f"GET /live_play?url={url}")

    stream_url = await get_stream_url(url)
    if not stream_url:
        raise HTTPException(
            status_code=404,
            detail={
                "error_type": 404,
                "error_message": "Не удалось получить поток",
            },
        )

    file_size, supports_range = await fetch_video_metadata(stream_url)
    content_type = "video/mp4"

    return JSONResponse(
        status_code=200,
        content={
            "stream_url": stream_url,
            "content_type": content_type,
            "supports_range": supports_range,
            "file_size": file_size,
        },
    )


@live_router.get("/stream", response_class=StreamingResponse)
@exception_handler()
async def stream_video(request: Request, stream_url: str) -> StreamingResponse:
    """Стримит видео по полученному URL"""
    file_size, supports_range = await fetch_video_metadata(stream_url)

    range_header = request.headers.get("Range")
    start, end = 0, file_size - 1 if file_size else None

    if range_header and supports_range:
        try:
            range_type, ranges = range_header.split("=")
            if range_type.strip() == "bytes":
                start, end = ranges.split("-")
                start = int(start)
                end = int(end) if end else file_size - 1
        except Exception as e:
            app_logger.warning(f"Invalid Range header in {stream_url}: {e}")

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": "video/mp4",
    }

    if supports_range:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        status_code = 206
    else:
        status_code = 200

    return StreamingResponse(
        stream_generator(
            start=start, end=end, supports_range=supports_range, stream_url=stream_url
        ),
        status_code=status_code,
        headers=headers,
        media_type="video/mp4",
    )
