"""workshop description

Revision ID: aab1d8b56c4f
Revises: dfd5b1ab0b63
Create Date: 2024-04-14 11:01:11.834039

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aab1d8b56c4f'
down_revision = 'dfd5b1ab0b63'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('workshop') as batch_op:
    batch_op.add_column(sa.Column('description', sa.Text,
                        nullable=True))


def downgrade():
  with op.batch_alter_table('workshop') as batch_op:
    batch_op.drop_column('description')
