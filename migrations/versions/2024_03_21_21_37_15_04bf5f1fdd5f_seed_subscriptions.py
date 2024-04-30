"""Seed subscriptions

Revision ID: 04bf5f1fdd5f
Revises: 0d1843648592
Create Date: 2024-03-21 21:37:15.601838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04bf5f1fdd5f'
down_revision = '0d1843648592'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('subscription', schema=None) as batch_op:
    batch_op.add_column(
        sa.Column('description', sa.String(255), nullable=True))
    batch_op.drop_column('duration')
    batch_op.add_column(
        sa.Column('type', sa.Enum('monthly', 'annually')))

  subscript_table = sa.table('subscription',
                             sa.column('id', sa.Integer),
                             sa.column('title', sa.String(255)),
                             sa.column('price', sa.Numeric(8, 2)),
                             sa.column('type', sa.Enum('monthly', 'annually')),
                             sa.column('description', sa.String(255))
                             )

  op.bulk_insert(subscript_table, [
      {
          'title': 'Monthly membership',
          'price': 5.00,
          'type': 'monthly',
          'description': 'Monthly membership subscription'
      },
      {
          'title': 'Annual membership',
          'price': 50.00,
          'type': 'annually',
          'description': 'Annual membership subscription'
      }
  ])


def downgrade():
  with op.batch_alter_table('subscription', schema=None) as batch_op:
    batch_op.drop_column('description')
    batch_op.add_column(
        sa.Column('duration', sa.Integer, nullable=True))
    batch_op.drop_column('type')

  table = sa.table('subscription')
  op.execute(table.delete())
