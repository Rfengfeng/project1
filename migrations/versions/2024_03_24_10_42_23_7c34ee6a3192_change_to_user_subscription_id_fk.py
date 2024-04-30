"""empty message

Revision ID: 7c34ee6a3192
Revises: 9de6d92ea078
Create Date: 2024-03-24 10:42:23.036189

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7c34ee6a3192'
down_revision = '9de6d92ea078'
branch_labels = None
depends_on = None


def upgrade():
  # ### commands auto generated by Alembic - please adjust! ###
  with op.batch_alter_table('payment', schema=None) as batch_op:

    batch_op.add_column(sa.Column('user_subscription_id',
                        sa.Integer(), nullable=True))
    batch_op.drop_constraint('payment_ibfk_2', type_='foreignkey')
    batch_op.create_foreign_key('fk_user_subscription_id_user_subscription_user_subscription_id', 'user_subscription', ['user_subscription_id'], [
                                'id'], onupdate='CASCADE', ondelete='CASCADE')
    batch_op.drop_column('subscription_id')

  # ### end Alembic commands ###


def downgrade():
  # ### commands auto generated by Alembic - please adjust! ###
  with op.batch_alter_table('payment', schema=None) as batch_op:

    batch_op.add_column(sa.Column(
        'subscription_id', mysql.INTEGER(), autoincrement=False, nullable=True))
    batch_op.drop_constraint(
        'fk_user_subscription_id_user_subscription_user_subscription_id', type_='foreignkey')
    batch_op.create_foreign_key('payment_ibfk_2', 'subscription', ['subscription_id'], [
                                'id'], onupdate='CASCADE', ondelete='CASCADE')
    batch_op.drop_column('user_subscription_id')

  # ### end Alembic commands ###
