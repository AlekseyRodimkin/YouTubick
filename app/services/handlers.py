import inspect
from functools import wraps
from fastapi import HTTPException, Request

from ..config import templates


def exception_handler():
    """Main route decorator"""

    def decorator(func):
        if inspect.iscoroutinefunction(func):

            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                try:
                    return await func(request, *args, **kwargs)
                except HTTPException as http_ex:
                    raise http_ex
                except Exception as e:
                    pass
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
                            "message": "Ошибка на стороне сервера",
                        },
                        status_code=500,
                    )

            return wrapper
        else:
            raise TypeError("This decorator only supports async functions")

    return decorator
