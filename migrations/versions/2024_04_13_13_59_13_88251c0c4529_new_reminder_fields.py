"""New reminder fields

Revision ID: 88251c0c4529
Revises: 19cc0bf1ff32
Create Date: 2024-04-13 13:59:13.019916

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '88251c0c4529'
down_revision = '19cc0bf1ff32'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('reminder') as batch_op:
    batch_op.add_column(sa.Column('booking_id', sa.Integer(), nullable=True))
    batch_op.create_foreign_key(
        'fk_reminder_booking_id', 'booking', ['booking_id'], ['id'], ondelete='SET NULL')
    batch_op.add_column(sa.Column('user_subscription_id',
                        sa.Integer(), nullable=True))
    batch_op.create_foreign_key(
        'fk_reminder_user_subscription_id', 'user_subscription', ['user_subscription_id'], ['id'], ondelete='SET NULL')
    batch_op.add_column(sa.Column('type', sa.Enum(
        'general', 'booking', 'subscription', name='reminder_type'), nullable=False, server_default='general'))


def downgrade():
  with op.batch_alter_table('reminder') as batch_op:
    batch_op.drop_constraint(
        'fk_reminder_user_subscription_id', type_='foreignkey')
    batch_op.drop_column('user_subscription_id')
    batch_op.drop_constraint('fk_reminder_booking_id', type_='foreignkey')
    batch_op.drop_column('booking_id')
    batch_op.drop_column('type')
