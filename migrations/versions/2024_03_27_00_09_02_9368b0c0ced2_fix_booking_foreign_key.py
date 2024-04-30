"""Fix booking foreign key

Revision ID: 9368b0c0ced2
Revises: 08834af2124a
Create Date: 2024-03-27 00:09:02.371720

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9368b0c0ced2'
down_revision = '08834af2124a'
branch_labels = None
depends_on = None


def upgrade():
  op.execute('''
    DELETE FROM booking WHERE schedule_id IS NULL;
  ''')
  with op.batch_alter_table('booking') as batch_op:
    batch_op.drop_constraint('booking_schedule_id_fkey', type_='foreignkey')
    batch_op.create_foreign_key('booking_schedule_id_fkey', 'schedule', [
                                'schedule_id'], ['id'], ondelete='CASCADE', onupdate='CASCADE')


def downgrade():
  with op.batch_alter_table('booking') as batch_op:
    batch_op.drop_constraint('booking_schedule_id_fkey', type_='foreignkey')
    batch_op.create_foreign_key(
        'booking_schedule_id_fkey', 'schedule', ['schedule_id'], ['id'])
  pass
