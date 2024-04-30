"""Unify payment status

Revision ID: 2dfa72a2cdd6
Revises: 915599781378
Create Date: 2024-04-20 12:26:49.542116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2dfa72a2cdd6'
down_revision = '915599781378'
branch_labels = None
depends_on = None


def upgrade():
  op.execute(
      "UPDATE payment SET status = 'completed' WHERE status IN ('success', 'Completed', 'confirmed')")

  op.execute(
      "UPDATE payment SET payment_type = 'credit_card' WHERE payment_type IN ('card', 'on')")
  with op.batch_alter_table('payment') as batch_op:
    batch_op.alter_column('status', type_=sa.Enum(
        'pending', 'completed', 'failed', 'refunded'))
    batch_op.add_column(sa.Column('refunded_at', sa.DateTime))
    batch_op.add_column(sa.Column('refunded_amount', sa.DECIMAL(10, 2)))


def downgrade():
  with op.batch_alter_table('payment') as batch_op:
    batch_op.drop_column('refunded_amount')
    batch_op.drop_column('refunded_at')
    batch_op.alter_column('status', type_=sa.String(32))
