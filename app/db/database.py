from sqlalchemy.ext.asyncio import AsyncSession, declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = "postgresql+asyncpg://admin:amir112233@localhost:5432/edumanager"


engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)



async def get_db():
    async with AsyncSessionLocal() as session:
    yield session
    