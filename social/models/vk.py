from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VkGroups(Base):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(sa.Integer)
    confirmation_token: Mapped[str] = mapped_column(sa.String)
    secret_key: Mapped[str] = mapped_column(sa.String)
    create_ts: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow)
    update_ts: Mapped[datetime] = mapped_column(sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
