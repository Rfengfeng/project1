"""Lesson description

Revision ID: dfe4f7a2712e
Revises: 349814d20430
Create Date: 2024-04-14 23:54:17.755651

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfe4f7a2712e'
down_revision = '349814d20430'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('lesson') as batch_op:
    batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))


def downgrade():
  with op.batch_alter_table('lesson') as batch_op:
    batch_op.drop_column('description')
