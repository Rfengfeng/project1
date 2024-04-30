"""Attendance

Revision ID: 880f05a7c6ea
Revises: dfd5b1ab0b63
Create Date: 2024-04-13 23:56:36.557903

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '880f05a7c6ea'
down_revision = 'dfd5b1ab0b63'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('booking') as batch_op:
    batch_op.add_column(sa.Column('attended', sa.Boolean,
                        nullable=False, server_default='0'))


def downgrade():
  with op.batch_alter_table('booking') as batch_op:
    batch_op.drop_column('attended')
