from fastapi import APIRouter, Request, Query
from config.logging_config import logger
from fastapi.responses import JSONResponse, StreamingResponse
from app.services.youtube import download_video
from app.services.utils import file_streamer
import os

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

        return JSONResponse(
            status_code=404,
            content={"message": "Файл не найден"}
        )

    except Exception as e:
        app_logger.error(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Внутренняя ошибка сервера"}
        )


@work_router.post("/long_play")
async def download(request: Request, url: str = Query(...)):
    try:
        app_logger.info(f"POST/long_play?url={url}")


    except Exception as e:
        app_logger.error(f"Error: {e}")
        return JSONResponse(
            status_code=500,
            content={"message": "Внутренняя ошибка сервера"}
        )