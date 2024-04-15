"""Create group request

Revision ID: 27dda7e6236a
Revises: 62addefd9655
Create Date: 2024-04-15 03:59:03.133907

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27dda7e6236a'
down_revision = '62addefd9655'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'create_group_request',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('secret_key', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('mapped_group_id', sa.Integer(), nullable=True),
        sa.Column('create_ts', sa.DateTime(), nullable=False),
        sa.Column('valid_ts', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ['mapped_group_id'],
            ['group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('create_group_request')
