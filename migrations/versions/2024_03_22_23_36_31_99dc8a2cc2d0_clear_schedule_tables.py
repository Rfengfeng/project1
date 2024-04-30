"""Clear schedule tables

Revision ID: 99dc8a2cc2d0
Revises: d2cfdc2cd69b
Create Date: 2024-03-22 23:36:31.712013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99dc8a2cc2d0'
down_revision = 'd2cfdc2cd69b'
branch_labels = None
depends_on = None


def upgrade():
  foreign_key_exists = op.get_bind().exec_driver_sql('''
    SELECT * FROM information_schema.TABLE_CONSTRAINTS WHERE
    CONSTRAINT_SCHEMA = DATABASE() AND
    TABLE_NAME        = 'booking' AND
    CONSTRAINT_NAME   = 'booking_ibfk_4' AND
    CONSTRAINT_TYPE   = 'FOREIGN KEY'
  ''').first()

  if foreign_key_exists:
    op.execute('''
      ALTER TABLE `booking` DROP FOREIGN KEY `booking_ibfk_4`;
    ''')

  foreign_key_exists = op.get_bind().exec_driver_sql('''
    SELECT * FROM information_schema.TABLE_CONSTRAINTS WHERE
    CONSTRAINT_SCHEMA = DATABASE() AND
    TABLE_NAME        = 'booking' AND
    CONSTRAINT_NAME   = 'booking_ibfk_5' AND
    CONSTRAINT_TYPE   = 'FOREIGN KEY'
  ''').first()

  if foreign_key_exists:
    op.execute('''
      ALTER TABLE `booking` DROP FOREIGN KEY `booking_ibfk_5`;
    ''')
  column_exists = op.get_bind().exec_driver_sql('''
    SELECT * FROM information_schema.COLUMNS WHERE
    TABLE_SCHEMA = DATABASE() AND
    TABLE_NAME   = 'booking' AND
    COLUMN_NAME  = 'lesson_schedule_id'
  ''').first()
  if column_exists:
    op.execute('ALTER TABLE `booking` DROP COLUMN `lesson_schedule_id`')

  column_exists = op.get_bind().exec_driver_sql('''
    SELECT * FROM information_schema.COLUMNS WHERE
    TABLE_SCHEMA = DATABASE() AND
    TABLE_NAME   = 'booking' AND
    COLUMN_NAME  = 'workshop_schedule_id'
  ''').first()

  if column_exists:
    op.execute('ALTER TABLE `booking` DROP COLUMN `workshop_schedule_id`')

  op.execute('DROP TABLE IF EXISTS lesson_schedule')
  op.execute('DROP TABLE IF EXISTS workshop_schedule')


def downgrade():
  op.create_table('lesson_schedule',
                  sa.Column('id', sa.Integer(), nullable=False),
                  sa.PrimaryKeyConstraint('id')
                  )

  op.create_table('workshop_schedule',
                  sa.Column('id', sa.Integer(), nullable=False),
                  sa.PrimaryKeyConstraint('id')
                  )

  with op.batch_alter_table('booking', schema=None) as batch_op:
    batch_op.add_column(sa.Column('lesson_schedule_id', sa.Integer()))
    batch_op.add_column(sa.Column('workshop_schedule_id', sa.Integer()))
    batch_op.create_foreign_key('booking_ibfk_4', 'lesson_schedule', [
                                'lesson_schedule_id'], ['id'])
    batch_op.create_foreign_key('booking_ibfk_5', 'workshop_schedule', [
                                'workshop_schedule_id'], ['id'])
