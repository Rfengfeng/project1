"""Add booking status

Revision ID: 08834af2124a
Revises: 7c34ee6a3192
Create Date: 2024-03-25 21:59:06.686014

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08834af2124a'
down_revision = '7c34ee6a3192'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('booking') as batch_op:
    batch_op.add_column(
        sa.Column('status', sa.Enum('pending', 'confirmed',
                  'cancelled'), nullable=False, default='pending')
    )
  op.execute('''
    UPDATE booking
    SET status = 'confirmed'
    WHERE confirmed = 1
'''
             )
  with op.batch_alter_table('booking') as batch_op:
    batch_op.drop_column('confirmed')


def downgrade():
  with op.batch_alter_table('booking') as batch_op:
    batch_op.add_column(
        sa.Column('confirmed', sa.BOOLEAN(), nullable=False, default=False)
    )

  op.execute('''
    UPDATE booking
    SET confirmed = 1
    WHERE status = 'confirmed'
'''
             )

  with op.batch_alter_table('booking') as batch_op:
    batch_op.drop_column('status')
