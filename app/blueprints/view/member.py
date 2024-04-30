
from flask import Blueprint, flash, redirect, url_for, render_template, request


from app.models.reminder import Reminder
from app.models.user import Role
from app.utils.hash import generate_password_hash, is_strong_password
from app.utils.session import get_current_user, require_membership

from app.models import User, Lesson, Schedule, Booking
from app.models.booking import BookingStatus

from app.database import db
from app.utils.string_helper import generate_salt
from datetime import datetime
from app.utils.session import get_current_user, require_login, require_roles

member_view = Blueprint('member_view', __name__)


@member_view.before_request
def check_user():
  current_user = get_current_user()
  if not current_user or current_user.role != Role.member.value:
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('user_view.login'))


@member_view.route('/listtutors', methods=['GET', 'POST'])
def list_tutors():
    # Pagination settings
  page = request.args.get('page', 1, type=int)
  per_page = 12  # Number of tutors per page
  if request.method == 'POST':
    # Get the search query from the form
    search_query = request.form.get('query')
    # Perform a search query if it's not empty
    if search_query:
      search_term = f'%{search_query}%'
      tutors = db.session.query(User).filter(
          (User.role == Role.tutor.value) &
          ((User.first_name.ilike(search_term)) |
           (User.last_name.ilike(search_term)) |
           ((User.first_name + " " + User.last_name).ilike(search_term)) |
           (User.email.ilike(search_term)))
      ).paginate(page=page, per_page=per_page)
      if not tutors.items:
        flash("No result found.", "danger")
    else:
      # If search query is empty, just retrieve all tutors
      tutors = db.session.query(User).filter_by(
          role=Role.tutor.value).paginate(page=page, per_page=per_page)
  else:
    # If it's a GET request or no search query provided, retrieve all tutors
    tutors = db.session.query(User).filter_by(
        role=Role.tutor.value).paginate(page=page, per_page=per_page)

  return render_template('member/list_tutors.html', tutors=tutors)


@member_view.route('/view_tutor_profile', methods=['GET'])
def view_tutor_profile():
  if request.method == 'GET':
    tutor_id = request.args.get('id')
    tutor = User.query.get(tutor_id)
    if not tutor:
      flash('Tutor not found.', 'danger')
      return redirect(url_for('member_view.list_tutors'))
    return render_template('member/tutor_profile.html', tutor=tutor)


@member_view.route('/lessonsbytutor', methods=['GET', 'POST'])
def lessonsbytutor():
  current_user = get_current_user()
  tutor_id = request.args.get('tutor_id')
  # tutor = db.session.query(User).filter(User.id == tutor_id).first()
  lessons = []

  if tutor_id:
    lessons = db.session.query(Lesson).filter(Lesson.tutor_id == tutor_id)

  if request.method == 'POST':
    search_query = request.form.get('search')
    if search_query:  # If search query is not empty
      search_term = f'%{search_query}%'
      lessons = db.session.query(Lesson).filter(
          tutor_id == tutor_id and Lesson.title.ilike(search_term)).all()
      if not lessons:  # If no result found
        flash("No result found.", "danger")

  return render_template('member/lessons_by_tutor.html', BookingStatus=BookingStatus, lessons=lessons, current_user=current_user, now=datetime.now())


@member_view.route('/all_lessons', methods=['GET', 'POST'])
def all_lessons():
  current_user = get_current_user()
  page = request.args.get('page', 1, type=int)  # Get the page number

  search_query = request.args.get('search')
  # Filter schedules that are lesson schedules
  filter = (Schedule.lesson_id.isnot(None))

  if search_query:
    search_term = f'%{search_query}%'
    # Filter schedules that have lessons with titles that match the search query
    filter = filter & Schedule.lesson.has(Lesson.title.ilike(search_term))

  schedules = db.session.query(Schedule).filter(
      filter
  ).order_by(
      Schedule.start_datetime.desc()
  ).paginate(page=page, per_page=10)
  return render_template('member/all_lessons.html', search_query=search_query, BookingStatus=BookingStatus, schedules=schedules, current_user=current_user, now=datetime.now())


@member_view.route('/book_lesson/<int:schedule_id>', methods=['GET', 'POST'])
@require_membership()
def book_lesson(schedule_id):
  # Get the schedule and the current user
  schedule = Schedule.query.get(schedule_id)
  current_user = get_current_user()
  if not schedule:
    flash('Invalid schedule ID.', 'danger')
    return redirect(url_for('member_view.all_lessons'))
  if schedule.bookings:
    flash('This schedule has already been booked.', 'danger')
    return redirect(url_for('member_view.all_lessons'))
  # Create a new booking
  booking = Booking(
      user_id=current_user.id,
      user=current_user,
      type="lesson",
      cost=schedule.cost,  # Assuming the cost is a numeric value
      amount_paid=0.00,  # Assuming the amount paid is a numeric value
      schedule_id=schedule_id,
      start_datetime=schedule.start_datetime,
      end_datetime=schedule.end_datetime,
      created_at=datetime.now()
  )
  # Add the booking to the database
  db.session.add(booking)
  db.session.commit()

  booking_id = booking.id
  booking = Booking.query.get(booking_id)

  return render_template('member/book_lesson.html', schedule=schedule, current_user=current_user, booking=booking, booking_id=booking_id)


@member_view.route('/list_workshop', methods=['GET'])
@require_login()  # Get the current logged-in user
def list_workshop():
  current_user = get_current_user()
  page = request.args.get('page', 1, type=int)
  if request.method == 'GET':
     # Query the database for schedules associated with workshops,
     # filtering out those without a workshop_id set
    schedules = db.session.query(Schedule).filter(
        Schedule.workshop_id.isnot(None)
    ).order_by(Schedule.start_datetime.desc()).paginate(
        page=page, per_page=10
    )
    # Get the current datetime
  current_datetime = datetime.now()
  # Render the HTML template with the retrieved schedules, current user, and current datetime
  return render_template('member/list_workshop.html', schedules=schedules, current_user=current_user, current_datetime=current_datetime)


@member_view.route('/add_booking/<int:id>', methods=['GET', 'POST'])
@require_login()
def add_booking(id: int):
  '''
  Book a workshop
  '''

  current_user = get_current_user()
  # Check if the user has an active membership
  if (not current_user.membership_expiry or current_user.membership_expiry < datetime.now()):
    flash('Please renew your membership before booking a workshop.', 'danger')
    # Redirect the user to the list of workshops
    return redirect(url_for('member_view.list_workshop'))

  current_schedule = db.session.query(Schedule).get(id)

  # Add a new booking
  booking = Booking(
      user_id=current_user.id,
      type='workshop',
      cost=current_schedule.workshop.price,
      start_datetime=current_schedule.start_datetime,
      end_datetime=current_schedule.end_datetime,
      schedule_id=current_schedule.id,
      status=BookingStatus.pending.value,
  )

  db.session.add(booking)
  db.session.commit()

  flash('Workshop booked successfully', 'success')
  return redirect(url_for('payment_view.booking_get', booking_id=booking.id))
