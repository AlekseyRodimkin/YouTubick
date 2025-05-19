from pathlib import Path
import redis
from aiofiles import os as aiofiles_os
from celery.result import AsyncResult
from fastapi import Request, HTTPException, Form
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.routing import APIRouter

from config.logging_config import logger
from app.services import file_streamer, exception_handler, extract_video_id, celery_task_download_video

download_router = APIRouter(prefix="", tags=["work"])
app_logger = logger.bind(name="app")
r = redis.Redis()


@download_router.get("/download")
@exception_handler()
async def redirect_download(request: Request, url: str):
    task = celery_task_download_video.delay(url)
    return RedirectResponse(url=f"/download/{task.id}", status_code=302)


@download_router.post("/download")
@exception_handler()
async def download_video(request: Request, url: str = Form(...)):
    video_id = extract_video_id(url=url)
    key = f"video:{video_id}"

    existing_task_id = r.get(key)
    if existing_task_id:
        task_id = existing_task_id.decode()
        return {
            "task_id": task_id,
            "status_url": f"/status/{task_id}",
            "download_url": f"/download/{task_id}"
        }

    task = celery_task_download_video.delay(url)
    return {
        "task_id": task.id,
        "status_url": f"/status/{task.id}",
        "download_url": f"/download/{task.id}"
    }


@download_router.get("/download/{task_id}")
@exception_handler()
async def get_video(request: Request, task_id: str):
    task = AsyncResult(task_id)
    if not task.ready():
        raise HTTPException(404, "File not ready")

    result = task.result
    if isinstance(result, dict):
        filename = result.get("filename")
    else:
        filename = result  # fallback

    if filename.endswith('.mp4') and await aiofiles_os.path.exists(filename):
        return StreamingResponse(
            file_streamer(filename),
            media_type='video/mp4',
            headers={"Content-Disposition": f"attachment; filename={Path(filename).name}"}
        )


@download_router.get("/status/{task_id}")
@exception_handler()
async def get_status(request: Request, task_id: str):
    return {"status": AsyncResult(task_id).state}
