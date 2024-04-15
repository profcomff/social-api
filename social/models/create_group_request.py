from datetime import UTC, datetime, timedelta

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .group import Group
from social.utils.string import random_string


class CreateGroupRequest(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    secret_key: Mapped[str] = mapped_column(default=lambda: random_string(32))
    owner_id: Mapped[int]
    mapped_group_id: Mapped[int | None] = mapped_column(sa.ForeignKey("group.id"))

    create_ts: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    valid_ts: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC) + timedelta(days=1))

    mapped_group: Mapped[Group | None] = relationship(Group)
