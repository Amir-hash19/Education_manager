from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.users.routes import router as userrouter
from app.bootcamp.routes import router as bootcamprouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.config import settings

# ---------------------------
# Lifespan context
# ---------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 🔹 راه‌اندازی Redis Cache
    redis_client = aioredis.from_url(settings.REDIS_URL)
    cache_backend = RedisBackend(redis_client)
    FastAPICache.init(cache_backend, prefix="fastapi-cache")
    


    yield 

 
    await redis_client.close()

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(
    title="Education Manager Project",
    description="Admin panel and bootcamp management",
    version="0.0.1",
    lifespan=lifespan,
    contact={
        "name": "Amirhosein Heidari",
        "url": "https://Amir-hash19.github.io",
        "email": "amirhosein.hydri1381@email.com",
    },
    license_info={"name": "MIT"},
    openapi_tags=[{"name": "Udemy clone", "description": "managing CRUD operations"}],
)

# ---------------------------
# Routers
# ---------------------------
app.include_router(userrouter, tags=["users"])
app.include_router(bootcamprouter, tags=["bootcamp"])
