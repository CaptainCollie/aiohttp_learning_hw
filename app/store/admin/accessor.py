import typing
from hashlib import sha256
from typing import Optional

from app.base.base_accessor import BaseAccessor
from app.admin.models import Admin

if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application"):
        await self.create_admin(
            email=self.app.config.admin.email,
            password=self.app.config.admin.password
        )

    async def get_by_email(self, email: str) -> Optional[Admin]:
        for admin in self.app.database.admins:
            if admin.email == email:
                return admin

    async def create_admin(self, email: str, password: str) -> Admin:
        admin = Admin(
            id=self.app.database.next_admin_id,
            email=email,
            password=sha256(password.encode()).hexdigest()
        )
        self.app.database.admins.append(admin)
        return admin
