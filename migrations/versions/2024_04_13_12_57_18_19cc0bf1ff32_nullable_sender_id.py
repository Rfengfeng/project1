"""Nullable sender id

Revision ID: 19cc0bf1ff32
Revises: eb1363d5ce64
Create Date: 2024-04-13 12:57:18.342038

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19cc0bf1ff32'
down_revision = 'eb1363d5ce64'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('reminder') as batch_op:
    batch_op.alter_column(
        'sender_id', existing_type=sa.Integer, nullable=True)
    batch_op.add_column(
        sa.Column('action_text', sa.String(length=255), nullable=True))
    batch_op.add_column(
        sa.Column('action_url', sa.String(length=255), nullable=True))


def downgrade():
  with op.batch_alter_table('reminder') as batch_op:
    batch_op.alter_column(
        'sender_id', existing_type=sa.Integer, nullable=False)
    batch_op.drop_column('action_text')
    batch_op.drop_column('action_url')
