"""Seed memberships

Revision ID: 915599781378
Revises: d985920bd1a3
Create Date: 2024-04-20 11:44:02.509313

"""
import datetime
import random
from re import sub
from alembic import op
import sqlalchemy as sa

from app.utils.string_helper import extract_user_address


# revision identifiers, used by Alembic.
revision = '915599781378'
down_revision = 'd985920bd1a3'
branch_labels = None
depends_on = None


def upgrade():
  members = op.get_bind().exec_driver_sql(
      'SELECT * FROM `user` WHERE `role` = "member" AND `membership_expiry` IS NULL').fetchall()

  user_subscription_table = sa.table(
      'user_subscription',
      sa.Column('user_id', sa.Integer),
      sa.Column('subscription_id', sa.Integer),
      sa.Column('start_datetime', sa.DateTime),
      sa.Column('end_datetime', sa.DateTime),
      sa.Column('cost', sa.DECIMAL(10, 2)),
      sa.Column('amount_paid', sa.DECIMAL(10, 2)),
  )
  payment_table = sa.table(
      'payment',
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
      sa.Column('user_subscription_id', sa.Integer),
  )

  initial_datetime = datetime.datetime(2023, 3, 18, 9, 0, 0)

  annually_subscription = op.get_bind().exec_driver_sql(
      'SELECT * FROM `subscription` WHERE `duration` > 360').fetchone()
  monthly_subscription = op.get_bind().exec_driver_sql(
      'SELECT * FROM `subscription` WHERE `duration` < 32').fetchone()

  # 3 anually memberships
  for j in range(3):
    member = random.choice(members)
    members.remove(member)
    subscription_start = initial_datetime + \
        datetime.timedelta(days=random.randint(1, 350))

    subscription_end = subscription_start + \
        datetime.timedelta(days=annually_subscription.duration)

    op.execute(
        user_subscription_table.insert().values(
            user_id=member.id,
            subscription_id=annually_subscription.id,
            start_datetime=subscription_start,
            end_datetime=subscription_start +
            datetime.timedelta(days=annually_subscription.duration),
            cost=annually_subscription.price,
            amount_paid=annually_subscription.price
        )
    )
    user_subscription_id = op.get_bind().exec_driver_sql(
        'SELECT LAST_INSERT_ID()').fetchone()[0]
    (address1, suburb, postcode) = extract_user_address(member)
    op.get_bind().exec_driver_sql('UPDATE `user` SET `membership_expiry` = %s WHERE `id` = %s', (
        subscription_end, member.id)
    )

    op.execute(
        payment_table.insert().values(
            first_name=member.first_name,
            last_name=member.last_name,
            email=member.email,
            address=address1,
            country='New Zealand',
            suburb=suburb,
            postcode=postcode,
            paid_at=subscription_start,
            status='confirmed',
            payment_type='credit_card',
            name_on_card=member.first_name + ' ' + member.last_name,
            card_number='4242',
            expiration_date='12/25',
            user_id=member.id,
            user_subscription_id=user_subscription_id
        )
    )
  # 4 random memberships each month
  for i in range(0, (datetime.datetime.now() - initial_datetime).days // 30):
    for j in range(4):
      member = random.choice(members)

      subscription_start = initial_datetime + \
          datetime.timedelta(days=random.randint(1, 28) + i * 30)
      subscription_end = subscription_start + \
          datetime.timedelta(days=monthly_subscription.duration)

      op.execute(
          user_subscription_table.insert().values(
              user_id=member.id,
              subscription_id=monthly_subscription.id,
              start_datetime=subscription_start,
              end_datetime=subscription_start +
              datetime.timedelta(days=monthly_subscription.duration),
              cost=monthly_subscription.price,
              amount_paid=monthly_subscription.price
          )
      )
      user_subscription_id = op.get_bind().exec_driver_sql(
          'SELECT LAST_INSERT_ID()').fetchone()[0]
      (address1, suburb, postcode) = extract_user_address(member)
      op.get_bind().exec_driver_sql('UPDATE `user` SET `membership_expiry` = %s WHERE `id` = %s', (
          subscription_end, member.id)
      )

      op.execute(
          payment_table.insert().values(
              first_name=member.first_name,
              last_name=member.last_name,
              email=member.email,
              address=address1,
              country='New Zealand',
              suburb=suburb,
              postcode=postcode,
              paid_at=subscription_start,
              status='confirmed',
              payment_type='credit_card',
              name_on_card=member.first_name + ' ' + member.last_name,
              card_number='4242',
              expiration_date='12/25',
              user_id=member.id,
              user_subscription_id=user_subscription_id
          )
      )


def downgrade():
  pass
