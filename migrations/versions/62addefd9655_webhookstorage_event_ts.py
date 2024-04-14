"""WebhookStorage event_ts

Revision ID: 62addefd9655
Revises: 1cacaf803a1d
Create Date: 2024-04-15 00:21:54.075449

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '62addefd9655'
down_revision = '1cacaf803a1d'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('webhook_storage', sa.Column('event_ts', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('webhook_storage', 'event_ts')
