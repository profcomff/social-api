"""vk

Revision ID: 9d98c1e9c864
Revises: 57c72962d2b4
Create Date: 2023-08-19 15:53:19.787309

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '9d98c1e9c864'
down_revision = '57c72962d2b4'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'vk_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('confirmation_token', sa.String(), nullable=False),
        sa.Column('secret_key', sa.String(), nullable=False),
        sa.Column('create_ts', sa.DateTime(), nullable=False),
        sa.Column('update_ts', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('vk_groups')
