"""Seed booking and reminders

Revision ID: 4f08229ed22d
Revises: c93676019c0e
Create Date: 2024-03-17 01:02:35.410231

"""
from datetime import datetime, timedelta
from email.policy import default
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4f08229ed22d'
down_revision = 'c93676019c0e'
branch_labels = None
depends_on = None


lesson_number = 'COMP639'
tutor_email = 'jane.doe@email.com'
member_email = 'harry.potter@email.com'


def upgrade():
  with op.batch_alter_table('lesson', schema=None) as batch_op:
    batch_op.add_column(sa.Column('lesson_number', sa.String(32)))

  table = sa.table('user', sa.sql.column('id', sa.Integer),
                   sa.sql.column('email', sa.String))
  member = op.get_bind().execute(
      table.select()
      .where(table.c.email == member_email)
  ).first()
  tutor = op.get_bind().execute(
      table.select()
      .where(table.c.email == tutor_email)
  ).first()

  lesson_table = sa.table(
      'lesson',
      sa.sql.column('id', sa.Integer),
      sa.sql.column('title', sa.String),
      sa.sql.column('tutor_id', sa.Integer),
      sa.sql.column('lesson_number', sa.String),
      sa.sql.column('cost', sa.Numeric),
  )

  op.bulk_insert(lesson_table, [
      {
          'title': 'Introduction to Merino',
          'tutor_id': tutor.id,
          'lesson_number': lesson_number,
          'cost': 100,
      }
  ])

  lesson = op.get_bind().execute(
      lesson_table.select()
      .where(lesson_table.c.tutor_id == tutor.id)
      .where(lesson_table.c.lesson_number == lesson_number)
      .order_by(lesson_table.c.id.desc())
  ).first()

  # bulk insert lesson schedule, on monday, wednesday, friday, 10:00 - 12:00, repeat until 2024-04-17
  data = []
  schedule_monday = datetime(2024, 3, 18)
  schedule_wednesday = datetime(2024, 3, 20)
  schedule_friday = datetime(2024, 3, 22)

  schedule_table = sa.table(
      'lesson_schedule',
      sa.sql.column('id', sa.Integer),
      sa.sql.column('lesson_id', sa.Integer),
      sa.sql.column('start_datetime', sa.DateTime),
      sa.sql.column('end_datetime', sa.DateTime),
      sa.sql.column('cost', sa.Numeric(8, 2)),
  )

  for i in range(1, 4):
    data.append({
        'lesson_id': lesson.id,
        'start_datetime': schedule_monday.replace(hour=10, minute=0, second=0),
        'end_datetime': schedule_monday.replace(hour=12, minute=0, second=0),
        'cost': 100,
    })
    data.append({
        'lesson_id': lesson.id,
        'start_datetime': schedule_wednesday.replace(hour=10, minute=0, second=0),
        'end_datetime': schedule_wednesday.replace(hour=12, minute=0, second=0),
        'cost': 100,
    })
    data.append({
        'lesson_id': lesson.id,
        'start_datetime': schedule_friday.replace(hour=10, minute=0, second=0),
        'end_datetime': schedule_friday.replace(hour=12, minute=0, second=0),
        'cost': 100,
    })
    schedule_monday += timedelta(days=7)
    schedule_wednesday += timedelta(days=7)
    schedule_friday += timedelta(days=7)
  op.bulk_insert(schedule_table, data)

  inserted_schedules = op.get_bind().execute(
      schedule_table.select()
      .where(schedule_table.c.lesson_id == lesson.id)
      .where(schedule_table.c.start_datetime >= datetime(2024, 3, 18))
      .where(schedule_table.c.start_datetime <= datetime(2024, 4, 27))
  ).fetchall()

  bookings = []
  booking_table = sa.table(
      'booking',
      sa.sql.column('id', sa.Integer),
      sa.sql.column('user_id', sa.Integer),
      sa.sql.column('cost', sa.Numeric(8, 2)),
      sa.sql.column('confirmed', sa.Boolean),
      sa.sql.column('start_datetime', sa.DateTime),
      sa.sql.column('end_datetime', sa.DateTime),
      sa.sql.column('amount_paid', sa.Numeric(8, 2)),
      sa.sql.column('type', sa.String),
      sa.sql.column('lesson_schedule_id', sa.Integer),
      sa.sql.column('created_at', sa.DateTime),
  )

  for schedule in inserted_schedules:
    bookings.append({
        'user_id': member.id,
        'cost': schedule.cost,
        'confirmed': True,
        'start_datetime': schedule.start_datetime,
        'end_datetime': schedule.end_datetime,
        'amount_paid': schedule.cost,
        'lesson_schedule_id': schedule.id,
        'type': 'lesson',
        'created_at': datetime.now(),
    })

  op.bulk_insert(booking_table, bookings)


def downgrade():
  table = sa.table('user', sa.sql.column('id', sa.Integer),
                   sa.sql.column('email', sa.String))
  tutor = op.get_bind().execute(
      table.select()
      .where(table.c.email == tutor_email)
  ).first()

  lesson_table = sa.table(
      'lesson',
      sa.sql.column('id', sa.Integer),
      sa.sql.column('tutor_id', sa.Integer),
      sa.sql.column('lesson_number', sa.String)
  )

  lesson = op.get_bind().execute(
      lesson_table.select()
      .where(lesson_table.c.tutor_id == tutor.id)
      .where(lesson_table.c.lesson_number == lesson_number)
  ).first()

  # get schedules
  schedule_table = sa.table(
      'lesson_schedule',
      sa.sql.column('id', sa.Integer),
      sa.sql.column('lesson_id', sa.Integer),
  )
  schedules = op.get_bind().execute(
      schedule_table.select()
      .where(schedule_table.c.lesson_id == lesson.id)
  ).fetchall()

  # delete member bookings
  booking_table = sa.table(
      'booking',
      sa.sql.column('id', sa.Integer),
      sa.sql.column('lesson_schedule_id', sa.Integer),
  )
  op.execute(
      booking_table.delete()
      .where(booking_table.c.lesson_schedule_id.in_([schedule.id for schedule in schedules]))
  )

  # delete schedules
  op.execute(
      schedule_table.delete()
      .where(schedule_table.c.lesson_id == lesson.id)
  )

  # delete lesson
  op.execute(
      lesson_table.delete()
      .where(lesson_table.c.id == lesson.id)
  )
  with op.batch_alter_table('lesson', schema=None) as batch_op:
    batch_op.drop_column('lesson_number')
