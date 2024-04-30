"""Snap payment amount

Revision ID: e964c1d5dc79
Revises: 2dfa72a2cdd6
Create Date: 2024-04-20 12:54:40.820432

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e964c1d5dc79'
down_revision = '2dfa72a2cdd6'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('payment') as batch_op:
    batch_op.add_column(
        sa.Column(
            'amount_paid', sa.DECIMAL(10, 2), nullable=False, server_default='0.00'
        )
    )

  op.execute(
      """
      UPDATE payment p
      INNER JOIN user_subscription us
      ON p.user_subscription_id = us.id
      SET p.amount_paid = us.amount_paid
      """
  )
  op.execute(
      """
      UPDATE payment p
      INNER JOIN booking b
      ON b.id = p.booking_id
      SET p.amount_paid = b.cost
      """
  )


def downgrade():
  with op.batch_alter_table('payment') as batch_op:
    batch_op.drop_column('amount_paid')
