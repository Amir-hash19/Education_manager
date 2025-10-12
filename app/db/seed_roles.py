from sqlalchemy import select
from .database import AsyncSessionLocal 
from app.users.models import RoleModel
import asyncio

async def seed_roles():
    async with AsyncSessionLocal() as session:
        roles = ["admin", "teacher", "student"]
        for role_name in roles:
            exists = await session.execute(
                select(RoleModel).where(RoleModel.name == role_name)
            )
            if not exists.scalar():
                session.add(RoleModel(name=role_name, description=f"{role_name} role"))
        await session.commit()

