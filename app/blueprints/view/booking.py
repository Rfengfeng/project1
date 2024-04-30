from email.policy import default
from flask import Blueprint, render_template, request, redirect, url_for, flash

from datetime import datetime
from app.models.booking import Booking
from app.models.schedule import Schedule
from app.utils.session import get_current_user, require_login

booking_view = Blueprint('booking_view', __name__)


@booking_view.route('/<int:id>', methods=['GET'])
@require_login()
def details(id: int):
  '''
  Get the details of a booking by ID
  '''
  booking = Booking.query.get(id)
  return render_template('booking/details.html', booking=booking)


@booking_view.route('/user', methods=['GET'], defaults={'id': 0})
@booking_view.route('/user/<int:id>', methods=['GET'])
@require_login()
def user_bookings(id: int):
  '''
  Get the bookings for a user by user ID or the current user
  '''
  if id == 0:
    id = get_current_user().id

  page = request.args.get('page', 1, type=int)

  # Get all bookings for the user that have not started yet
  bookings = Booking.query.filter(
      (Booking.schedule_id != None) &
      (Booking.user_id == id) &
      (Booking.start_datetime >= datetime.today()) & (
          (Booking.schedule.has(Schedule.lesson_id != None)) |
          (Booking.schedule.has(Schedule.workshop_id != None))
      )
  ).order_by(
      Booking.start_datetime.desc()
  ).paginate(page=page, per_page=10)

  return render_template('user/bookings.html', bookings=bookings, now=datetime.now())
