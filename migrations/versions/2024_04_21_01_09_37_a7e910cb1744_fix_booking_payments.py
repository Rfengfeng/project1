"""Fix booking payments

Revision ID: a7e910cb1744
Revises: e964c1d5dc79
Create Date: 2024-04-21 01:09:37.466475

"""
from alembic import op
import sqlalchemy as sa

from app.models.payment import PaymentStatus
from app.utils.string_helper import extract_user_address


# revision identifiers, used by Alembic.
revision = 'a7e910cb1744'
down_revision = 'e964c1d5dc79'
branch_labels = None
depends_on = None


def upgrade():
  unpaid_bookings = op.get_bind().exec_driver_sql(
      "SELECT * FROM booking WHERE status = 'confirmed' AND id NOT IN (SELECT booking_id FROM payment WHERE booking_id IS NOT NULL)"
  ).fetchall()

  if not unpaid_bookings:
    return

  user_ids = [str(booking.user_id) for booking in unpaid_bookings]

  users_data = op.get_bind().exec_driver_sql(
      f"SELECT * FROM user WHERE id IN ({','.join(user_ids)})",
  ).fetchall()

  users = {}

  for d in users_data:
    users[str(d.id)] = d

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
      sa.Column('booking_id', sa.Integer),
      sa.Column('amount_paid', sa.DECIMAL(10, 2)),
  )

  for booking in unpaid_bookings:
    user = users[str(booking.user_id)]
    (address, suburb, postcode) = extract_user_address(user)
    op.execute(
        payment_table.insert().values(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            address=address,
            country='New Zealand',
            suburb=suburb,
            postcode=postcode,
            paid_at=booking.created_at,
            status=PaymentStatus.completed.value,
            payment_type='credit-card',
            name_on_card=user.first_name + ' ' + user.last_name,
            card_number='4242',
            expiration_date='12/25',
            user_id=user.id,
            booking_id=booking.id,
            amount_paid=booking.cost
        )
    )


def downgrade():
  pass
