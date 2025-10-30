"""Init user & task

Revision ID: d0530c284d5c
Revises: 
Create Date: 2025-10-29 17:38:26.331965
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd0530c284d5c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # 表已存在，只给 task 增加 user_id 外键
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_task_user_id', 'user', ['user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_constraint('fk_task_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')