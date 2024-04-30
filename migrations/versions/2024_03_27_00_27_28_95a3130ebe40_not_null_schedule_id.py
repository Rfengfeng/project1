"""Not null schedule id

Revision ID: 95a3130ebe40
Revises: 9368b0c0ced2
Create Date: 2024-03-27 00:27:28.423078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '95a3130ebe40'
down_revision = '9368b0c0ced2'
branch_labels = None
depends_on = None


def upgrade():
  op.execute('''
    DELETE FROM booking WHERE schedule_id IS NULL;
  ''')
  op.execute('SET FOREIGN_KEY_CHECKS = 0;')
  with op.batch_alter_table('booking') as batch_op:
    batch_op.alter_column('schedule_id', existing_type=sa.INTEGER(),
                          nullable=False)
  op.execute('SET FOREIGN_KEY_CHECKS = 1;')


def downgrade():
  op.execute('SET FOREIGN_KEY_CHECKS = 0;')
  with op.batch_alter_table('booking') as batch_op:
    batch_op.alter_column('schedule_id', existing_type=sa.INTEGER(),
                          nullable=True)
  op.execute('SET FOREIGN_KEY_CHECKS = 1;')
