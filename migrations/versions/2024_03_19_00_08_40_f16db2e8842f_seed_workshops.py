"""Seed workshops

Revision ID: f16db2e8842f
Revises: 9ba4f4707a32
Create Date: 2024-03-18 23:37:40.409352

"""
from datetime import datetime, timedelta
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f16db2e8842f'
down_revision = 'e6d1960fcf59'
branch_labels = None
depends_on = None

tutor_email = 'jane.doe@email.com'
member_email = 'harry.potter@email.com'

booking_table = sa.table('booking',
                         sa.sql.column('id', sa.Integer),
                         sa.sql.column('user_id', sa.Integer),
                         sa.sql.column('cost', sa.Numeric),
                         sa.sql.column('confirmed', sa.Boolean),
                         sa.sql.column('start_datetime', sa.DateTime),
                         sa.sql.column('end_datetime', sa.DateTime),
                         sa.sql.column('amount_paid', sa.Numeric),
                         sa.sql.column('workshop_schedule_id', sa.Integer),
                         sa.sql.column('type', sa.String),
                         sa.sql.column('created_at', sa.DateTime)
                         )


workshop_table = sa.table('workshop',
                          sa.sql.column('id', sa.Integer),
                          sa.sql.column('title', sa.String),
                          sa.sql.column('location_id', sa.Integer),
                          sa.sql.column('price', sa.Numeric),
                          )

location_table = sa.table('location',
                          sa.sql.column('id', sa.Integer),
                          sa.sql.column('title', sa.String),
                          sa.sql.column('address1', sa.String),
                          sa.sql.column('suburb', sa.String),
                          sa.sql.column('region', sa.String),
                          sa.sql.column('postcode', sa.String),
                          )

user_table = sa.table('user',
                      sa.sql.column('id', sa.Integer),
                      sa.sql.column('email', sa.String),
                      )


def upgrade():

  member = op.get_bind().execute(
      user_table.select()
      .where(user_table.c.email == member_email)
  ).first()
  tutor = op.get_bind().execute(
      user_table.select()
      .where(user_table.c.email == tutor_email)
  ).first()

  op.bulk_insert(location_table, [
      {
          'title': 'Lincoln University Campus',
          'address1': '85084 Ellesmere Junction Road',
          'suburb': 'Lincoln',
          'region': 'Canterbury',
          'postcode': '7647',
      }
  ])

  location = op.get_bind().execute(location_table
                                   .select()
                                   .where(location_table.c.title == 'Lincoln University Campus')
                                   .order_by(location_table.c.id.desc())
                                   ).first()

  op.bulk_insert(workshop_table, [
      {
          'title': 'Merino at Lincoln',
          'location_id': location.id,
          'price': 100,
      }
  ])
  workshop = op.get_bind().execute(workshop_table
                                   .select()
                                   .where(workshop_table.c.title == 'Merino at Lincoln')
                                   .order_by(workshop_table.c.id.desc())
                                   ).first()

  # bulk insert workshop schedule, on monday, Thursday, 2:00 - 4:00pn, repeat until 2024-04-17
  data = []
  schedule_monday = datetime(2024, 3, 18)
  schedule_thursday = datetime(2024, 3, 21)

  schedule_table = sa.table('workshop_schedule',
                            sa.sql.column('id', sa.Integer),
                            sa.sql.column('workshop_id', sa.Integer),
                            sa.sql.column('start_datetime', sa.DateTime),
                            sa.sql.column('end_datetime', sa.DateTime),
                            sa.sql.column('tutor_id', sa.Integer)
                            )

  for i in range(1, 4):
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

  inserted_schedules = op.get_bind().execute(
      schedule_table.select()
      .where(schedule_table.c.workshop_id == workshop.id)
  ).fetchall()

  bookings = []

  for schedule in inserted_schedules:
    bookings.append({
        'user_id': member.id,
        'cost': 0,
        'confirmed': True,
        'start_datetime': schedule.start_datetime,
        'end_datetime': schedule.end_datetime,
        'amount_paid': 0,
        'workshop_schedule_id': schedule.id,
        'type': 'workshop',
        'created_at': datetime.now(),
    })

  op.bulk_insert(booking_table, bookings)


def downgrade():
  table = user_table
  tutor = op.get_bind().execute(
      table.select()
      .where(table.c.email == tutor_email)
  ).first()

  workshop = op.get_bind().execute(
      workshop_table.select()
      .where(workshop_table.c.title == 'Merino at Lincoln')
  ).first()

  # get schedules
  schedule_table = sa.table('workshop_schedule',
                            sa.sql.column('id', sa.Integer),
                            sa.sql.column('workshop_id', sa.Integer),
                            sa.sql.column('tutor_id', sa.Integer)
                            )

  schedules = op.get_bind().execute(
      schedule_table.select()
      .where(schedule_table.c.workshop_id == workshop.id)
      .where(schedule_table.c.tutor_id == tutor.id)
  ).fetchall()

  # delete member bookings
  op.execute(
      booking_table.delete()
      .where(booking_table.c.workshop_schedule_id.in_([schedule.id for schedule in schedules]))
  )

  # delete schedules
  op.execute(
      schedule_table.delete()
      .where(schedule_table.c.workshop_id == workshop.id)
  )

  # delete lesson
  op.execute(
      workshop_table.delete()
      .where(workshop_table.c.id == workshop.id)
  )
