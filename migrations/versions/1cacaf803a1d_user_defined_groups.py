"""User defined groups

Revision ID: 1cacaf803a1d
Revises: 9d98c1e9c864
Create Date: 2024-04-14 23:38:18.956845

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1cacaf803a1d'
down_revision = '9d98c1e9c864'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'group',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('activation_token', sa.String(), nullable=True),
        sa.Column('create_ts', sa.DateTime(), nullable=False),
        sa.Column('update_ts', sa.DateTime(), nullable=False),
    )
    op.execute('''
        INSERT INTO "group"
            (id, type, is_deleted, is_active, create_ts, update_ts)
        SELECT id, 'vk_group', False, False, create_ts, update_ts
        FROM vk_groups;
    ''')
    op.create_primary_key('group_pk', 'group', ['id'])
    op.create_table(
        'telegram_channel',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['id'],
            ['group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'telegram_chat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['id'],
            ['group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'vk_chat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['id'],
            ['group.id'],
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_foreign_key('group_vkgroup_fk', 'vk_groups', 'group', ['id'], ['id'])
    op.drop_column('vk_groups', 'update_ts')
    op.drop_column('vk_groups', 'create_ts')
    op.execute('DROP SEQUENCE IF EXISTS vk_groups_id_seq;')
    op.rename_table('vk_groups', 'vk_group')


def downgrade():
    op.rename_table('vk_group', 'vk_groups')
    op.add_column('vk_groups', sa.Column('create_ts', sa.DateTime()))
    op.add_column('vk_groups', sa.Column('update_ts', sa.DateTime()))
    op.execute('UPDATE vk_groups SET create_ts = (SELECT create_ts FROM "group" WHERE "group".id = vk_groups.id);')
    op.execute('UPDATE vk_groups SET update_ts = (SELECT update_ts FROM "group" WHERE "group".id = vk_groups.id);')
    op.alter_column('vk_groups', 'create_ts', nullable=False)
    op.alter_column('vk_groups', 'update_ts', nullable=False)
    op.drop_constraint('group_vkgroup_fk', 'vk_groups', type_='foreignkey')
    op.drop_table('vk_chat')
    op.drop_table('telegram_chat')
    op.drop_table('telegram_channel')
    op.drop_table('group')
