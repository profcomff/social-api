from enum import Enum

import sqlalchemy as sa
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship

from .base import Base


class WebhookSystems(str, Enum):
    TELEGRAM = 'telegram'
    GITHUB = 'github'


class WebhookStorage(Base):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    system: Mapped[WebhookSystems] = mapped_column(sa.Enum(WebhookSystems, native_enum=False))
    message: Mapped[sa.JSON] = mapped_column(sa.JSON(True))
