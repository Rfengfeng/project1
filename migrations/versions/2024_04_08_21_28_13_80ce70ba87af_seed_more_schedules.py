"""Seed more schedules

Revision ID: 80ce70ba87af
Revises: d3c88b5ca09a
Create Date: 2024-04-08 21:28:13.596300

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta


# revision identifiers, used by Alembic.
revision = '80ce70ba87af'
down_revision = 'd3c88b5ca09a'
branch_labels = None
depends_on = None


def upgrade():
  workshop = op.get_bind().exec_driver_sql(
      'SELECT * FROM `workshop` LIMIT 1').first()
  tutor = op.get_bind().exec_driver_sql(
      'SELECT * FROM `user` WHERE `role` = "tutor" LIMIT 1').first()
  # bulk insert workshop schedule, on monday, Thursday, 2:00 - 4:00pn, repeat until 2024-04-17
  data = []
  schedule_monday = datetime(2024, 3, 18)
  schedule_thursday = datetime(2024, 3, 21)

  schedule_table = sa.table('schedule',
                            sa.sql.column('id', sa.Integer),
                            sa.sql.column('workshop_id', sa.Integer),
                            sa.sql.column('start_datetime', sa.DateTime),
                            sa.sql.column('end_datetime', sa.DateTime),
                            sa.sql.column('tutor_id', sa.Integer)
                            )

  for i in range(1, 20):
    data.append({
        'workshop_id': workshop.id,
        'start_datetime': schedule_monday.replace(hour=13, minute=0, second=0),
        'end_datetime': schedule_monday.replace(hour=15, minute=0, second=0),
        'tutor_id': tutor.id,
    })
    data.append({
        'workshop_id': workshop.id,
        'start_datetime': schedule_thursday.replace(hour=14, minute=0, second=0),
        'end_datetime': schedule_thursday.replace(hour=16, minute=0, second=0),
        'tutor_id': tutor.id,
    })
    schedule_monday += timedelta(days=7)
    schedule_thursday += timedelta(days=7)

  op.bulk_insert(schedule_table, data)


def downgrade():
  schedule_monday = datetime(2024, 4, 8).strftime('%Y-%m-%d')
  op.execute(
      f"DELETE FROM `schedule` WHERE `start_datetime` > '{schedule_monday}'")
