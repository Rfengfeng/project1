"""Membership expiry

Revision ID: dfd5b1ab0b63
Revises: 88251c0c4529
Create Date: 2024-04-13 14:07:07.649229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfd5b1ab0b63'
down_revision = '88251c0c4529'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('user') as batch_op:
    batch_op.add_column(sa.Column('membership_expiry',
                        sa.DateTime(), nullable=True))


def downgrade():
  with op.batch_alter_table('user') as batch_op:
    batch_op.drop_column('membership_expiry')
