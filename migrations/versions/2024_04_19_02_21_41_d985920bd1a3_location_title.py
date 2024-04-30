"""Location title

Revision ID: d985920bd1a3
Revises: 3d7c04372f30
Create Date: 2024-04-19 02:21:41.893737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd985920bd1a3'
down_revision = '3d7c04372f30'
branch_labels = None
depends_on = None


def upgrade():
  op.execute(
      "UPDATE `location` SET `title` = CONCAT(`suburb`, ' Campus') WHERE `title` IS NULL")


def downgrade():
  pass
