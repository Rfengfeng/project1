"""Subscription duration

Revision ID: 76bf068dd527
Revises: 371caaf2597c
Create Date: 2024-04-17 21:26:42.488133

"""
from http import server
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76bf068dd527'
down_revision = '371caaf2597c'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('subscription') as batch_op:
    batch_op.add_column(sa.Column('duration', sa.Integer(),
                        nullable=False, server_default='0'))

  op.execute('UPDATE subscription SET duration = 31 WHERE `type` = \'monthly\'')
  op.execute('UPDATE subscription SET duration = 365 WHERE `type` = \'annually\'')

  with op.batch_alter_table('subscription') as batch_op:
    batch_op.drop_column('type')


def downgrade():
  with op.batch_alter_table('subscription') as batch_op:
    batch_op.add_column(sa.Column('type', sa.Enum('monthly', 'annually'),
                        nullable=False, server_default='monthly'))

  op.execute('UPDATE subscription SET type = \'monthly\' WHERE duration = 31')
  op.execute(
      'UPDATE subscription SET type = \'annually\' WHERE duration = 365')

  with op.batch_alter_table('subscription') as batch_op:
    batch_op.drop_column('duration')
