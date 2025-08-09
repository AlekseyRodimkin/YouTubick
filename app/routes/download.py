from pathlib import Path

import redis
from aiofiles import os as aiofiles_os
from celery.result import AsyncResult
from fastapi import Form, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from starlette.responses import JSONResponse

from app.services import (
    celery_task_download_video,
    exception_handler,
    extract_video_id,
    file_streamer,
)
from config import logger, REDIS_HOST, REDIS_PORT

download_router = APIRouter(prefix="", tags=["work"])
app_logger = logger.bind(name="app")
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


@download_router.post("/download", status_code=200, response_class=JSONResponse)
@exception_handler()
async def download(request: Request, url: str = Form(...)) -> dict:
    """
    Эндпоинт загрузки.
    Запускает задачу по скачиванию и отправке email уведомления о запросе.
    Возвращает Json с информацией о задаче скачивания.
    """
    app_logger.info(f"POST/download: {url}")

    video_id = extract_video_id(url=url)
    key = f"video:{video_id}"

    existing_task_id = r.get(key)
    if existing_task_id:
        task_id = existing_task_id.decode()
        return {
            "task_id": task_id,
            "status_url": f"/status/{task_id}",
            "download_url": f"/download/{task_id}",
        }

    download_task = celery_task_download_video.delay(url)

    return {
        "task_id": download_task.id,
        "status_url": f"/status/{download_task.id}",
        "download_url": f"/download/{download_task.id}",
    }


@download_router.get(
    "/download/{task_id}", status_code=200, response_class=StreamingResponse
)
@exception_handler()
async def get_video(request: Request, task_id: str):
    """ "Эндпоинт получения файла"""
    app_logger.info(f"GET/download/{task_id}")

    task = AsyncResult(task_id)
    if not task.ready():
        raise HTTPException(404, "File not ready")

    result = task.result
    if isinstance(result, dict):
        filename = result.get("filename")
    else:
        filename = result

    if filename.endswith(".mp4") and await aiofiles_os.path.exists(filename):
        return StreamingResponse(
            file_streamer(filename),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename={Path(filename).name}"
            },
        )
    else:
        app_logger.warning(f"Файл не найден: {filename}")
        raise HTTPException(404, "File not found")


@download_router.get("/status/{task_id}", status_code=200, response_class=JSONResponse)
@exception_handler()
async def get_status(request: Request, task_id: str) -> dict:
    """Эндпоинт статуса задачи"""
    return {"status": AsyncResult(task_id).state}
