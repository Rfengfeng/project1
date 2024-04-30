"""Seed schedules

Revision ID: eeb9fed57adc
Revises: 25cb48f7327a
Create Date: 2024-04-19 00:47:22.992620

"""
from datetime import datetime, timedelta
from decimal import Decimal
import random
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eeb9fed57adc'
down_revision = '25cb48f7327a'
branch_labels = None
depends_on = None


def upgrade():
  op.execute(
      'DELETE FROM `schedule` WHERE `id` NOT IN (SELECT `schedule_id` FROM `booking`)')
  workshops = op.get_bind().exec_driver_sql(
      'SELECT * FROM `workshop`').fetchall()
  tutors = op.get_bind().exec_driver_sql(
      'SELECT * FROM `user` WHERE `role` = "tutor"').fetchall()
  lessons = op.get_bind().exec_driver_sql(
      'SELECT * FROM `lesson`').fetchall()

  # bulk insert workshop schedule, on monday, Thursday, 2:00 - 4:00pn, repeat until 2024-04-17
  data = []
  schedule_monday = datetime(2023, 3, 20)

  schedule_table = sa.table('schedule',
                            sa.Column('workshop_id', sa.Integer,
                                      nullable=True),
                            sa.Column('lesson_id', sa.Integer, nullable=True),
                            sa.Column('start_datetime', sa.DateTime),
                            sa.Column('end_datetime', sa.DateTime),
                            sa.Column('tutor_id', sa.Integer),
                            sa.Column('cost', sa.DECIMAL(10, 2))
                            )

  for i in range(1, 68):
    for j in range(1, 3):
      workshop = random.choice(workshops)
      tutor = random.choice(tutors)
      hour_start = random.randint(8, 12)

      schedule_day = schedule_monday + timedelta(days=random.randint(0, 4))

      data.append({
          'workshop_id': workshop.id,
          'lesson_id': None,
          'start_datetime': schedule_day.replace(hour=hour_start, minute=0, second=0),
          'end_datetime': schedule_day.replace(hour=hour_start + 1, minute=0, second=0),
          'tutor_id': tutor.id,
          'cost': workshop.price
      })
      lesson = random.choice(lessons)
      tutor = random.choice(tutors)

      hour_start = random.randint(12, 16)

      schedule_day = schedule_monday + timedelta(days=random.randint(0, 4))

      data.append({
          'workshop_id': None,
          'lesson_id': lesson.id,
          'start_datetime': schedule_day.replace(hour=hour_start, minute=0, second=0),
          'end_datetime': schedule_day.replace(hour=hour_start + 1, minute=0, second=0),
          'tutor_id': tutor.id,
          'cost': lesson.cost
      })

    schedule_monday += timedelta(days=7)

  op.bulk_insert(schedule_table, data)


def downgrade():
  pass  # no need to downgrade
