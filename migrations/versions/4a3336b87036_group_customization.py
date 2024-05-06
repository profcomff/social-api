"""Group customization

Revision ID: 4a3336b87036
Revises: 27dda7e6236a
Create Date: 2024-04-27 18:42:55.905145

"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = '4a3336b87036'
down_revision = '27dda7e6236a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('group', sa.Column('name', sa.String(), nullable=True))
    op.add_column('group', sa.Column('description', sa.String(), nullable=True))
    op.add_column('group', sa.Column('invite_link', sa.String(), nullable=True))
    op.add_column('group', sa.Column('hidden', sa.Boolean(), nullable=True))
    op.execute('UPDATE "group" SET hidden = false;')
    op.alter_column('group', 'hidden', nullable=False)


def downgrade():
    op.drop_column('group', 'hidden')
    op.drop_column('group', 'invite_link')
    op.drop_column('group', 'description')
    op.drop_column('group', 'name')
