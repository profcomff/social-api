"""webhook storage

Revision ID: 57c72962d2b4
Revises:
Create Date: 2023-03-12 14:22:34.958257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57c72962d2b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'webhook_storage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('system', sa.Enum('TELEGRAM', 'GITHUB', name='webhooksystems', native_enum=False), nullable=False),
        sa.Column('message', sa.JSON(none_as_null=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('webhook_storage')
