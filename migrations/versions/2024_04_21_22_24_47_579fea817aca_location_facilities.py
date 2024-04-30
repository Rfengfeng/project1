"""location facilities

Revision ID: 579fea817aca
Revises: a7e910cb1744
Create Date: 2024-04-21 22:24:47.712265

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579fea817aca'
down_revision = 'a7e910cb1744'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('location') as batch_op:
    batch_op.add_column(sa.Column('facilities', sa.Text(), nullable=True))


def downgrade():
  with op.batch_alter_table('location') as batch_op:
    batch_op.drop_column('facilities')
