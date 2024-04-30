from datetime import datetime
from tomlkit import value
from app.models.booking import Booking, BookingStatus
from app.models.user import User
from app.database import db


def get_booking_attendance(user: User, type: str):
  '''
    Get the attendance statistics for a user and booking type
    :param user: The user to get the statistics for
    :param type: The type of booking to get the statistics for
  '''

  # Filter the bookings by user, type, past start date, and confirmed status
  filter = (Booking.user_id == user.id) & (
      Booking.type == type
  ) & (
      Booking.start_datetime < datetime.now()
  ) & (
      Booking.status == BookingStatus.confirmed.value)

  # Get the total number of bookings
  total_bookings = db.session.query(Booking).filter(
      filter
  ).count()

  # Get the total number of attended bookings
  total_attended = db.session.query(Booking).filter(
      filter & (Booking.attended == True)
  ).count()

  # Get the last 10 bookings
  last_10_bookings = db.session.query(Booking).filter(
      (Booking.user_id == user.id) & (Booking.type == type)
  ).order_by(
      Booking.created_at.desc()).limit(10).all()

  return (total_bookings, total_attended, last_10_bookings)
