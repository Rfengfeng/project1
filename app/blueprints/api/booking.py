
from datetime import datetime
from flask import Blueprint, current_app, request

from app.database import db
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.reminder import Reminder
from app.models.user import Role
from app.utils.session import get_current_user, require_login, require_roles


booking_api = Blueprint('booking_api', __name__)


@booking_api.route('/<int:id>/cancel', methods=['POST'])
@require_login()
def cancel_booking(id: int):
  '''
  Cancel a booking by booking ID
  '''
  booking = db.session.query(Booking).get(id)

  user = get_current_user()
  # Check if the user is the booking owner or a manager
  if user.id != booking.user_id and user.role != Role.manager.value and booking.schedule.tutor_id != user.id:
    return {'success': False, 'message': 'You are not allowed to cancel this booking.'}

  if booking.start_datetime < datetime.now():
    return {'success': False, 'message': 'This booking has already started and cannot be cancelled.'}

  booking.status = BookingStatus.cancelled.value

  db.session.merge(booking)
  db.session.flush()

  reminder = Reminder.create_booking_reminder(booking)

  # Refund the payment if it exists
  payment = db.session.query(Payment).filter(Payment.booking_id == id).first()
  if payment:
    payment.status = PaymentStatus.refunded.value
    payment.refunded_at = datetime.now()
    payment.refunded_amount = payment.amount_paid
    db.session.merge(payment)
    reminder.content += f' Refund of ${payment.amount_paid} has been processed.'

  # Send the reminder to the user who made the booking
  if (user.id != booking.user_id):
    reminder.sender_id = user.id

  db.session.add(reminder)
  db.session.commit()
  return {'success': True, 'message': 'Booking cancelled successfully.'}


@booking_api.route('/<int:id>/confirm', methods=['POST'])
@require_login()
def confirm_booking(id: int):
  '''
  Confirm a booking by booking ID
  '''
  booking = db.session.query(Booking).get(id)
  user = get_current_user()
  # Check if the user is the schedule owner or a manager
  if user.role != Role.manager.value and booking.schedule.tutor_id != user.id:
    return {'success': False, 'message': 'You are not allowed to confirm this booking.'}

  booking.status = BookingStatus.confirmed.value

  db.session.merge(booking)
  db.session.flush()
  reminder = Reminder.create_booking_reminder(booking)
  if (user.id != booking.user_id):
    reminder.sender_id = user.id

  db.session.add(reminder)
  db.session.commit()
  return {'success': True, 'message': 'Booking confirmed.'}


@booking_api.route('/<int:id>/attend', methods=['POST'])
@require_roles([Role.manager, Role.tutor])
def attend_booking(id: int):
  '''
  Mark a booking as attended by booking ID
  '''

  booking = db.session.query(Booking).get(id)
  current_user = get_current_user()

  # Check if the booking has started
  if booking.start_datetime > datetime.now():
    return {'success': False, 'message': 'This booking has not started yet.'}

  # Check if the user is the schedule owner or a manager
  if booking.schedule.tutor_id != current_user.id and current_user.role != Role.manager.value:
    return {'success': False, 'message': 'You are not allowed to mark this booking as attended.'}

  booking.attended = True
  db.session.merge(booking)
  db.session.commit()
  return {'success': True, 'message': 'Attendance recorded.'}


@booking_api.route('/attend', methods=['POST'])
@require_roles([Role.manager, Role.tutor])
def attend_bookings():
  '''
  Mark multiple bookings as attended
  '''
  booking_ids = request.form.getlist('booking_ids', type=int)
  attended_bookings = []
  current_user = get_current_user()

  for id in booking_ids:
    booking = db.session.query(Booking).get(id)

    # Check if the booking has started
    if not booking or booking.start_datetime > datetime.now():
      continue

    # Check if the user is the schedule owner or a manager
    if booking.schedule.tutor_id != current_user.id and current_user.role != Role.manager.value:
      continue

    booking.attended = True
    attended_bookings.append(booking)
    db.session.merge(booking)

  if attended_bookings:
    db.session.commit()

  return {'success': True, 'message': 'Attendance recorded.', 'attended_bookings': [
      booking.id for booking in attended_bookings
  ]}
