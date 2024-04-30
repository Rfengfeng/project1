"""Seed bookings

Revision ID: 3d7c04372f30
Revises: eeb9fed57adc
Create Date: 2024-04-19 01:11:24.658654

"""
import datetime
import random
from alembic import op
import sqlalchemy as sa

from app.utils.string_helper import extract_user_address


# revision identifiers, used by Alembic.
revision = '3d7c04372f30'
down_revision = 'eeb9fed57adc'
branch_labels = None
depends_on = None


def upgrade():
  booking_table = sa.table(
      'booking',
      sa.Column('user_id', sa.Integer),
      sa.Column('type', sa.String),
      sa.Column('cost', sa.DECIMAL(8, 2)),
      sa.Column('amount_paid', sa.DECIMAL(8, 2)),
      sa.Column('start_datetime', sa.DateTime),
      sa.Column('end_datetime', sa.DateTime),
      sa.Column('created_at', sa.DateTime),
      sa.Column('schedule_id', sa.Integer),
      sa.Column('status', sa.Enum('pending', 'confirmed', 'cancelled')),
      sa.Column('attended', sa.Boolean)
  )
  payment_table = sa.table(
      'payment',
      sa.Column('id', sa.Integer),
      sa.Column('first_name', sa.String),
      sa.Column('last_name', sa.String),
      sa.Column('email', sa.String),
      sa.Column('address', sa.String),
      sa.Column('country', sa.String),
      sa.Column('suburb', sa.String),
      sa.Column('postcode', sa.String),
      sa.Column('paid_at', sa.DateTime),
      sa.Column('status', sa.String),
      sa.Column('payment_type', sa.String),
      sa.Column('name_on_card', sa.String),
      sa.Column('card_number', sa.String),
      sa.Column('expiration_date', sa.String),
      sa.Column('user_id', sa.Integer),
      sa.Column('booking_id', sa.Integer),
  )

  members = op.get_bind().exec_driver_sql(
      "SELECT * FROM `user` WHERE `role` = 'member'").fetchall()

  lesson_schedules = op.get_bind().exec_driver_sql(
      """
      SELECT * FROM `schedule`
        WHERE `lesson_id` IS NOT NULL
        AND `id` NOT IN (SELECT `schedule_id` FROM `booking`)
      """).fetchall()
  workshop_schedules = op.get_bind().exec_driver_sql(
      """
      SELECT * FROM `schedule`
        WHERE `workshop_id` IS NOT NULL
        AND `id` NOT IN (SELECT `schedule_id` FROM `booking`)
      """).fetchall()

  for schedule in lesson_schedules:
    if schedule.start_datetime > datetime.datetime.now():
      if random.choice([True, False]):
        continue

    member = random.choice(members)

    booking_data = {
        'user_id': member.id,
        'type': 'lesson',
        'cost': schedule.cost,
        'amount_paid': schedule.cost,
        'start_datetime': schedule.start_datetime,
        'end_datetime': schedule.end_datetime,
        'created_at': schedule.start_datetime,
        'schedule_id': schedule.id,
        'status': 'confirmed',
        'attended': random.choice([True, False]) if schedule.start_datetime < datetime.datetime.now() else False
    }

    op.bulk_insert(booking_table, [booking_data])
    booking_id = op.get_bind().exec_driver_sql(
        'SELECT last_insert_id() as cnt'
    ).fetchone().cnt
    (address1, suburb, postcode) = extract_user_address(member)
    payment = {
        'first_name': member.first_name,
        'last_name': member.last_name,
        'email': member.email,
        'address': address1,
        'country': 'New Zealand',
        'suburb': suburb,
        'postcode': postcode,
        'paid_at': schedule.start_datetime - datetime.timedelta(days=1),
        'status': 'success',
        'payment_type': 'card',
        'name_on_card': member.first_name + ' ' + member.last_name,
        'card_number': '4242',
        'expiration_date': '12/25',
        'user_id': member.id,
        'booking_id': booking_id
    }
    op.bulk_insert(payment_table, [payment])

  for schedule in workshop_schedules:
    if schedule.start_datetime > datetime.datetime.now():
      if random.choice([True, False]):
        continue

    removed_members = []
    for j in range(0, random.randint(1, 7)):
      member = random.choice(members)
      members.remove(member)
      removed_members.append(member)

      booking_data = {
          'user_id': member.id,
          'type': 'workshop',
          'cost': schedule.cost,
          'amount_paid': schedule.cost,
          'start_datetime': schedule.start_datetime,
          'end_datetime': schedule.end_datetime,
          'created_at': schedule.start_datetime,
          'schedule_id': schedule.id,
          'status': 'confirmed',
          'attended': random.choice([True, False]) if schedule.start_datetime < datetime.datetime.now() else False
      }
      op.bulk_insert(booking_table, [booking_data])
      booking_id = op.get_bind().exec_driver_sql(
          'SELECT last_insert_id() as cnt'
      ).fetchone().cnt
      (address1, suburb, postcode) = extract_user_address(member)
      payment = {
          'first_name': member.first_name,
          'last_name': member.last_name,
          'email': member.email,
          'address': address1,
          'country': 'New Zealand',
          'suburb': suburb,
          'postcode': postcode,
          'paid_at': schedule.start_datetime - datetime.timedelta(days=1),
          'status': 'success',
          'payment_type': 'card',
          'name_on_card': member.first_name + ' ' + member.last_name,
          'card_number': '4242',
          'expiration_date': '12/25',
          'user_id': member.id,
          'booking_id': booking_id
      }
      op.bulk_insert(payment_table, [payment])

    members = members + removed_members


def downgrade():
  pass
