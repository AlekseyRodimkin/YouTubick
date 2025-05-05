import os
from fastapi.templating import Jinja2Templates
from dotenv import find_dotenv, load_dotenv

# if not find_dotenv():
#     exit("Not exists .env")
# else:
#     load_dotenv()

# DB_HOST = os.getenv("DB_HOST", "postgres")
# DB_NAME = os.getenv("DB_NAME", "mydatabase")
# DB_USER = os.getenv("DB_USER", "user")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
# REDIS_HOST = os.getenv("REDIS_HOST", "redis")

templates = Jinja2Templates(directory="/home/aleksei/PycharmProjects/youtube_video/app/static/templates")

# for docker app
# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# for local app
# DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@localhost:5432/{DB_NAME}"

# engine = create_async_engine(DATABASE_URL, echo=True)
# async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
# Base = declarative_base()
#
# celery_app = Celery(
#     "fastapi_app",
#     # broker="redis://localhost:6379/0",
#     # backend="redis://localhost:6379/0",
#     broker=f"redis://{REDIS_HOST}:6379/0",
#     backend=f"redis://{REDIS_HOST}:6379/0",
#     include=["app.services.yandex"],
# )

# celery_app.conf.update(
#     broker_connection_retry_on_startup=True,
#     broker_connection_retry=True,
# )


# async def init_db():
#     """Creating tables at start"""
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#
#
# async def get_db() -> AsyncSession:
#     """Get DB session"""
#     async with async_session() as session:
#         yield session
