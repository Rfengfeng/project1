"""Merge Migrations

Revision ID: 349814d20430
Revises: 880f05a7c6ea, aab1d8b56c4f
Create Date: 2024-04-14 11:07:10.036577

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '349814d20430'
down_revision = ('880f05a7c6ea', 'aab1d8b56c4f')
branch_labels = None
depends_on = None


def upgrade():
  pass


def downgrade():
  pass
