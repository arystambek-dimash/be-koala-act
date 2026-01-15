import asyncio
import os

from sqlalchemy.dialects.postgresql import insert

from src.app.config import settings
from src.app.database import make_engine, make_sessionmaker
from src.models.users import User

ADMIN_EMAIL = os.getenv("SEED_ADMIN_EMAIL", "arystambekdimash005@gmail.com")


async def main():
    engine = make_engine(settings.db_url)
    Session = make_sessionmaker(engine)

    async with Session() as session:
        stmt = insert(User).values(
            email=ADMIN_EMAIL,
            full_name="Admin",
            is_admin=True,
        ).on_conflict_do_update(index_elements=[User.email], set_={"is_admin": True}).returning(User.id)

        res = await session.execute(stmt)
        await session.commit()

        created_id = res.scalar_one_or_none()
        if created_id:
            print(f"✅ Admin created: {ADMIN_EMAIL} (id={created_id})")
        else:
            print(f"ℹ️ Admin already exists: {ADMIN_EMAIL}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
