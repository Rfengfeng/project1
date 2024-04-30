"""image created at

Revision ID: d3c88b5ca09a
Revises: 39c90ad9923c
Create Date: 2024-04-08 00:51:02.496956

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3c88b5ca09a'
down_revision = '39c90ad9923c'
branch_labels = None
depends_on = None


def upgrade():
  op.execute('''
    UPDATE `image` SET `created_at` = NOW() WHERE `created_at` IS NULL;
             ''')
  with op.batch_alter_table('image') as batch_op:
    batch_op.alter_column('created_at', existing_type=sa.DateTime(),
                          nullable=False,
                          server_default=sa.text('now()'))


def downgrade():
  with op.batch_alter_table('image') as batch_op:
    batch_op.alter_column(
        'created_at', existing_type=sa.DateTime(), nullable=True),
