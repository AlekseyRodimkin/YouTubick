import inspect
import traceback

from fastapi import HTTPException, Request
from functools import wraps

from config.logging_config import logger
from config.config import templates

app_logger = logger.bind(name="app")


def exception_handler():
    """Main route decorator"""

    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                try:
                    return await func(request, *args, **kwargs)
                except HTTPException as http_ex:
                    app_logger.error(f"Error HTTP: {http_ex.detail}")
                    raise http_ex
                except Exception as e:
                    # app_logger.error(f"Unhandled error: {str(e)}", exc_info=True)
                    app_logger.error(f"Unhandled error: {traceback.format_exc()}")

                    db = kwargs.get("db") or next(
                        (arg for arg in args if hasattr(arg, "rollback")), None
                    )  # rollback
                    if db:
                        await db.rollback()
                    return templates.TemplateResponse(
                        "error.html",
                        {
                            "request": request,
                            "code": 500,
                            "message": "Ошибка на стороне сервера"
                        },
                        status_code=500
                    )

            return wrapper
        else:
            raise TypeError("This decorator only supports async functions")

    return decorator
