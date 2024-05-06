from datetime import UTC, datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Group(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str]
    owner_id: Mapped[int | None]

    name: Mapped[str | None]
    description: Mapped[str | None]
    invite_link: Mapped[str | None]
    hidden: Mapped[bool] = mapped_column(default=True)

    is_deleted: Mapped[bool] = mapped_column(default=False)
    last_active_ts: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))

    create_ts: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
    update_ts: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    __mapper_args__ = {
        "polymorphic_on": "type",
    }


class VkGroup(Group):
    id: Mapped[int] = mapped_column(sa.ForeignKey("group.id"), primary_key=True)
    group_id: Mapped[int]
    confirmation_token: Mapped[str]
    secret_key: Mapped[str]

    __mapper_args__ = {
        "polymorphic_identity": "vk_group",
    }


class VkChat(Group):
    id: Mapped[int] = mapped_column(sa.ForeignKey("group.id"), primary_key=True)
    peer_id: Mapped[int]

    __mapper_args__ = {
        "polymorphic_identity": "vk_chat",
    }


class TelegramChannel(Group):
    id: Mapped[int] = mapped_column(sa.ForeignKey("group.id"), primary_key=True)
    channel_id: Mapped[int] = mapped_column(sa.BigInteger)

    __mapper_args__ = {
        "polymorphic_identity": "tg_channel",
    }


class TelegramChat(Group):
    id: Mapped[int] = mapped_column(sa.ForeignKey("group.id"), primary_key=True)
    chat_id: Mapped[int] = mapped_column(sa.BigInteger)

    __mapper_args__ = {
        "polymorphic_identity": "tg_chat",
    }
