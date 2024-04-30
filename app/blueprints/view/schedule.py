from flask import Blueprint, flash, redirect, render_template, url_for

from app.models.booking import Booking, BookingStatus
from app.models.schedule import Schedule
from app.models.user import Role
from app.models.workshop import Workshop
from app.utils.session import require_roles
from app.database import db


schedule_view = Blueprint('schedule_view', __name__)


@schedule_view.route('/<int:id>/attendance', methods=['GET'])
@require_roles([Role.manager, Role.tutor])
def attendance(id: int):
  '''
  View the attendance for a schedule
  '''
  schedule = db.session.query(Schedule).get(id)
  if not schedule:

    flash('Schedule not found', 'danger')
    # should redrect to schedule list page
    return redirect(url_for('user_view.dashboard'))

  bookings = db.session.query(Booking).filter(
      (Booking.schedule_id == id)
      & (Booking.status == BookingStatus.confirmed.value)
  ).all()

  return render_template('schedule/attendance.html', bookings=bookings, schedule=schedule)


@schedule_view.route('/workshop/<int:workshop_id>', methods=['GET'])
def view_workshop_description(workshop_id):
  '''
  View the description for a workshop
  '''
  workshop = db.session.query(Workshop).filter_by(id=workshop_id).first()
  return render_template('manager/view_workshop_description.html', workshop=workshop)
