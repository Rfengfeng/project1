"""Update column name

Revision ID: eb1363d5ce64
Revises: 80ce70ba87af
Create Date: 2024-04-11 00:11:29.566154

"""
from calendar import c
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb1363d5ce64'
down_revision = '80ce70ba87af'
branch_labels = None
depends_on = None


def upgrade():
  with op.batch_alter_table('reminder') as batch_op:
    batch_op.alter_column(
        'remind_at', existing_type=sa.DateTime, new_column_name='reminded_at', nullable=False)
    try:
      batch_op.drop_constraint('reminder_ibfk_1', type_='foreignkey')
      batch_op.create_foreign_key('fk_reminder_sender_id_user_id', 'user', [
          'sender_id'], ['id'])
    except:
      print('Constraint already exists')

    try:
      batch_op.drop_constraint('reminder_ibfk_2', type_='foreignkey')
      batch_op.create_foreign_key('fk_reminder_receiver_id_user_id', 'user', [
          'receiver_id'], ['id'])
    except:
      print('Constraint already exists')


def downgrade():
  with op.batch_alter_table('reminder') as batch_op:
    batch_op.alter_column(
        'reminded_at', existing_type=sa.DateTime, new_column_name='remind_at')
    try:
      batch_op.drop_constraint(
          'fk_reminder_sender_id_user_id', type_='foreignkey')
      batch_op.create_foreign_key('reminder_ibfk_1', 'user', [
          'sender_id'], ['id'])
    except:
      print('Constraint already exists')

    try:
      batch_op.drop_constraint(
          'fk_reminder_receiver_id_user_id', type_='foreignkey')
      batch_op.create_foreign_key('reminder_ibfk_2', 'user', [
          'receiver_id'], ['id'])
    except:
      print('Constraint already exists')
