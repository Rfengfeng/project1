"""Add foreign key to booking

Revision ID: 60386b321635
Revises: 04bf5f1fdd5f
Create Date: 2024-03-22 21:16:36.110637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60386b321635'
down_revision = '04bf5f1fdd5f'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('booking', schema=None) as batch_op:
    batch_op.create_foreign_key(
        'booking_schedule_id_fkey', 'schedule', ['schedule_id'], ['id'])


def downgrade():
  with op.batch_alter_table('booking', schema=None) as batch_op:
    batch_op.drop_constraint('booking_schedule_id_fkey', type_='foreignkey')
