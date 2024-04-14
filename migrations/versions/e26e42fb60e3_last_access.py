"""Last access

Revision ID: e26e42fb60e3
Revises: 62addefd9655
Create Date: 2024-04-15 00:43:27.419968

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e26e42fb60e3'
down_revision = '62addefd9655'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('group', sa.Column('last_active_ts', sa.DateTime(), nullable=True))
    op.drop_column('group', 'activation_token')
    op.drop_column('group', 'is_active')


def downgrade():
    op.add_column('group', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('group', sa.Column('activation_token', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('group', 'last_active_ts')
