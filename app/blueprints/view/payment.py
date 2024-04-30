from flask import Blueprint, flash, redirect, url_for, render_template, request
import re
from app.models.payment import PaymentStatus
from app.models.reminder import Reminder
from app.models.user import Role
from app.utils.hash import generate_password_hash, is_strong_password
from app.utils.session import get_current_user
from app.models import User, Lesson, Schedule, Booking, Payment
from app.models.booking import BookingStatus
from app.database import db
from app.utils.string_helper import generate_salt
from datetime import datetime, timezone

payment_view = Blueprint('payment_view', __name__)


@payment_view.route('/booking/<int:booking_id>', methods=['POST'])
def booking_post(booking_id):
  '''
  Process the payment for a booking
  '''
  current_user = get_current_user()
  user_id = current_user.id
  booking = Booking.query.get(booking_id)

  # Gether the payment information
  first_name = request.form.get('firstName')
  last_name = request.form.get('lastName')
  email = request.form.get('email')
  address = request.form.get('address')
  address2 = request.form.get('address2')
  country = request.form.get('country')
  state = request.form.get('state')
  suburb = request.form.get('suburb')
  postcode = request.form.get('postcode')
  payment_type = request.form.get('paymentMethod')
  cc_name = request.form.get('cc-name')
  cc_number = request.form.get(
      'cc-number', '').replace(' ', '').replace('-', '')
  cc_expiration = request.form.get('cc-expiration')

  card_pattern = re.compile(r'^\d{13,19}$')
  # Validate the credit card number
  if not card_pattern.match(cc_number):
    flash('Please check the credit card number.', 'danger')
    return render_template('member/pay_booking.html', current_user=current_user, user_id=user_id, booking_id=booking_id, booking=booking)

  # Update the booking status and create the payment
  booking.amount_paid = booking.cost
  booking.status = BookingStatus.confirmed.value
  db.session.flush()

  payment = Payment(
      user_id=user_id,
      booking_id=booking_id,
      first_name=first_name,
      last_name=last_name,
      email=email,
      address=address,
      address2=address2,
      country=country,
      state=state,
      suburb=suburb,
      postcode=postcode,
      payment_type=payment_type,
      name_on_card=cc_name,
      card_number=cc_number[-4:],
      expiration_date=cc_expiration,
      paid_at=datetime.now(timezone.utc),
      status=PaymentStatus.completed.value,
      amount_paid=booking.cost,
  )
  db.session.add(payment)

  # Create a reminder for the booking
  reminder = Reminder.create_booking_reminder(booking)
  db.session.add(reminder)

  db.session.commit()
  flash('Payment successful!', 'success')
  return redirect(url_for('booking_view.user_bookings'))


@payment_view.route('/booking/<int:booking_id>', methods=['GET'])
def booking_get(booking_id):
  '''
  Show the payment form for a booking
  '''
  current_user = get_current_user()
  user_id = current_user.id
  booking = Booking.query.get(booking_id)

  if not user_id or not booking:
    flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('member_view.book_lesson', user_id=user_id))

  if booking.status == BookingStatus.confirmed.value:
    flash('This booking has already been paid.', 'danger')
    return redirect(url_for('member_view.all_lessons'))
  return render_template('member/pay_booking.html', current_user=current_user, user_id=user_id, booking_id=booking_id, booking=booking)
