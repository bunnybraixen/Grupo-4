import asyncio
from sqlalchemy import select
from app.database import get_session_maker
from app.models import User, UserRole
from app.services.auth_service import hash_password

async def main():
    async with get_session_maker()() as db:
        for email, password, full_name, role in [
            ("dev@corestream.com", "DevPassword123!", "Dev Tester", UserRole.DEVELOPER),
            ("admin@corestream.com", "AdminPassword123!", "Administrador", UserRole.ADMIN),
        ]:
            existing = await db.execute(select(User).where(User.email == email))
            user = existing.scalar_one_or_none()
            if user:
                print("Ya existe:", email)
                continue
            db.add(User(
                email=email,
                full_name=full_name,
                hashed_password=hash_password(password),
                role=role,
                is_active=True,
            ))
        await db.commit()
        print("Usuarios creados correctamente")

asyncio.run(main())
