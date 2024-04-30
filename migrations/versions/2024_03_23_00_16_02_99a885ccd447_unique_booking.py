"""Unique booking

Revision ID: 99a885ccd447
Revises: 99dc8a2cc2d0
Create Date: 2024-03-23 00:16:02.271020

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99a885ccd447'
down_revision = '99dc8a2cc2d0'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('booking', schema=None) as batch_op:
    batch_op.create_unique_constraint(
        'uq_booking_user_id_schedule_id', ['user_id', 'schedule_id'])


def downgrade():
  with op.batch_alter_table('booking', schema=None) as batch_op:
    batch_op.drop_constraint('uq_booking_user_id_schedule_id', type_='unique')
