import aiohttp

from fastapi import Request, Query, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter

from config.logging_config import logger
from app.services import get_stream_url, fetch_video_metadata, exception_handler

work_router = APIRouter(prefix="", tags=["work"])
app_logger = logger.bind(name="app")


@work_router.get("/live_play")
@exception_handler()
async def fast_play(request: Request, url: str = Query(...)):
    app_logger.info(f"GET /fast_play?url={url}")

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

    range_header = request.headers.get('Range')
    start, end = 0, file_size - 1 if file_size else None

    if range_header and supports_range:
        try:
            range_type, ranges = range_header.split('=')
            if range_type.strip() == 'bytes':
                start, end = ranges.split('-')
                start = int(start)
                end = int(end) if end else file_size - 1
        except Exception as e:
            app_logger.warning(f"Invalid Range header: {e}")

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Type": "video/mp4",
    }

    if supports_range:
        headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        status_code = 206
    else:
        status_code = 200

    async def stream_generator():
        timeout = aiohttp.ClientTimeout(total=3600)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            req_headers = {"Range": f"bytes={start}-{end}"} if supports_range else {}

            async with session.get(stream_url, headers=req_headers) as resp:
                if resp.status not in (200, 206):
                    raise aiohttp.ClientError(f"Invalid response status: {resp.status}")

                async for chunk in resp.content.iter_chunked(1024 * 8):  # 8KB chunks
                    yield chunk

    return StreamingResponse(
        stream_generator(),
        status_code=status_code,
        headers=headers,
        media_type="video/mp4"
    )
