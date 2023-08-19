from enum import Enum

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class WebhookSystems(str, Enum):
    TELEGRAM = 'telegram'
    GITHUB = 'github'
    VK = 'vk'


class WebhookStorage(Base):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    system: Mapped[WebhookSystems] = mapped_column(sa.Enum(WebhookSystems, native_enum=False))
    message: Mapped[sa.JSON] = mapped_column(sa.JSON(True))
