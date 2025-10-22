from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.users.routes import router as userrouter
from app.bootcamp.routes import router as bootcamprouter
from app.support.routes import router as supportrouter
from app.blog.routes import router as blogrouter
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from app.config import settings
from app.users.routes import create_bootstrap_admin
from app.db.database import AsyncSessionLocal



@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = await aioredis.from_url(settings.REDIS_URL, encoding="utf8", decode_responses=True)
    cache_backend = RedisBackend(redis_client)
    FastAPICache.init(cache_backend, prefix="fastapi-cache")
    
    
    async with AsyncSessionLocal() as db:
        await create_bootstrap_admin(db)
    
    yield
    
    await redis_client.close()



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





app.include_router(userrouter, tags=["users"])
app.include_router(bootcamprouter, tags=["bootcamps"])
app.include_router(blogrouter, tags=["blogs"])
app.include_router(supportrouter, tags=["supports"])