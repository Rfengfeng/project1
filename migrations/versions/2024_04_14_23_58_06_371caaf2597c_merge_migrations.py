"""merge_migrations

Revision ID: 371caaf2597c
Revises: a508955bfe3f, dfe4f7a2712e
Create Date: 2024-04-14 23:58:06.489107

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '371caaf2597c'
down_revision = ('a508955bfe3f', 'dfe4f7a2712e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
