from config.logging_config import logger
from app.services.youtube import download_video
from app.services.utils import file_streamer, delete_file
from fastapi import Request, Query, Response, status
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
import os
from starlette.background import BackgroundTask


work_router = APIRouter(prefix="", tags=["work"])
app_logger = logger.bind(name="app")


@work_router.post("/download")
async def download(request: Request, url: str = Query(...)):
    try:
        app_logger.info(f"POST/download?url={url}")

        result = await download_video(url)
        if result.endswith('.mp4') and os.path.exists(result):
            return StreamingResponse(
                file_streamer(result),
                media_type='video/mp4',
                headers={"Content-Disposition": f"attachment; filename={os.path.basename(result)}"}
            )

        # todo возврат ошибки (файл не найден)
        return 404

    except Exception as e:
        app_logger.error(f"Error: {e}")

        # todo возврат ошибки
        return 500


@work_router.get("/long_play")
async def long_play(request: Request, url: str = Query(...)):
    try:
        app_logger.info(f"POST/long_play?url={url}")

        file_path = await download_video(url)
        if not os.path.exists(file_path):
            # todo возврат ошибки (файл не найден)
            pass

        file_size = os.path.getsize(file_path)
        range_header = request.headers.get("range")
        byte1, byte2 = 0, file_size - 1

        if range_header:
            try:
                range_value = range_header.strip().split("=")[1]
                byte1, byte2 = range_value.split("-")
                byte1 = int(byte1)
                byte2 = int(byte2) if byte2 else file_size - 1
            except Exception as e:
                # todo
                app_logger.error(f"Ошибка парсинга Range: {e}")
                return Response(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE)

        chunk_size = byte2 - byte1 + 1

        def file_range_generator(path, start, length):
            with open(path, "rb") as f:
                f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(8192, remaining))
                    if not chunk:
                        break
                    yield chunk
                    remaining -= len(chunk)

        headers = {
            "Content-Range": f"bytes {byte1}-{byte2}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "video/mp4"
        }

        return StreamingResponse(
            file_range_generator(file_path, byte1, chunk_size),
            status_code=206 if range_header else 200,
            headers=headers,
            background=BackgroundTask(delete_file, file_path)
        )

    except Exception as e:
        app_logger.error(f"Error: {e}")

        # todo возврат ошибки
        return 500