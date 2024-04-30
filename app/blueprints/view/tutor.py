from sqlalchemy import desc, func, case, literal_column
import re
from datetime import datetime, timedelta, date
from flask import (
    Blueprint, request, render_template, flash, session, redirect, url_for,
)

from app.models import User, Schedule, Workshop
from app.database import db
from app.models.booking import Booking
from app.models.lesson import Lesson
from app.models.reminder import Reminder
from app.models.user import Role
from app.utils.datetime import exist_overlap
from app.utils.session import get_current_user, require_login, require_roles
from datetime import datetime

tutor_view = Blueprint('tutor_view', __name__)


@tutor_view.route('/manage_lesson_schedule', methods=['GET', 'POST'])
def manage_lesson_schedule():
  tutor = get_current_user()
  tutor_id = tutor.id
  lessons_query = Lesson.query.filter(Lesson.tutor_id == tutor_id)

  # Handle search functionality
  search_query = request.args.get('search')
  page = request.args.get('page', 1, type=int)

  filter = (Schedule.tutor_id == tutor_id) & (Schedule.lesson_id.isnot(None))
  # Append search query
  if search_query:
    filter = filter & (Schedule.lesson.has(
        Lesson.title.ilike(f'%{search_query}%')))

  lesson_schedules = db.session.query(Schedule).filter(
      filter
  ).order_by(
      Schedule.start_datetime.desc()
  ).paginate(page=page, per_page=10)

  if not len(lesson_schedules.items):
    flash("No result found.", "danger")

  if request.method == 'POST':
    action = request.form.get('action')

    if action == 'delete_selected':
      # Handle deletion of selected schedules
      delete_ids = request.form.getlist('delete_ids[]')
      if not delete_ids:
        flash('Please select schedules first.', 'danger')
      else:
        for schedule_id in delete_ids:
          schedule = db.session.query(Schedule).filter(
              Schedule.id == schedule_id).first()
          db.session.delete(schedule)
          db.session.commit()
          flash('Selected schedules have been deleted.', 'success')
    else:
      # Handle saving data to the database for the selected schedule
      schedule_id = request.form.get('selected_schedule_id')
      if schedule_id:
        schedule = db.session.query(Schedule).get(schedule_id)
        if schedule:
          start_datetime_str = request.form.get(
              f'start_datetime_{schedule.id}')
          end_datetime_str = request.form.get(f'end_datetime_{schedule.id}')

        # Convert string to datetime objects
          start_datetime = datetime.strptime(
              start_datetime_str, '%Y-%m-%dT%H:%M')
          end_datetime = datetime.strptime(
              end_datetime_str, '%Y-%m-%dT%H:%M')

          # Perform validation checks
          if start_datetime < datetime.now():
            flash("Start time must be later than now.", "danger")
          elif start_datetime >= end_datetime:
            flash("End time must be later than start time.", "danger")
          elif exist_overlap(start_datetime, end_datetime, tutor_id, schedule_id):
            flash("Intended schedule time overlaps with current schedule.", "danger")
          else:
            # Update the start and end datetimes of the current schedule
            schedule.start_datetime = start_datetime
            schedule.end_datetime = end_datetime
            # Commit changes only for the current schedule

            db.session.merge(schedule)
            db.session.commit()
            flash('Changes have been saved.', 'success')

  return render_template('tutor/manage_lesson_schedule.html', lesson_schedules=lesson_schedules, now=datetime.now())


@tutor_view.route('/create_lesson_schedule', methods=['GET', 'POST'])
def create_lesson_schedule():

  if request.method == 'POST':
    option = request.form.get('option')
    # go to different page based on the option selected
    if option == 'new_lesson':
      return redirect(url_for('tutor_view.create_schedule_new_lesson'))
    elif option == 'existing_lesson':
      return redirect(url_for('tutor_view.create_schedule_existing_lesson'))
    else:
      flash('Please choose an option.')
      return render_template('tutor/create_lesson_schedule.html')

  return render_template('tutor/create_lesson_schedule.html')


@tutor_view.route('/create_schedule_existing_lesson', methods=['GET', 'POST'])
def create_schedule_existing_lesson():
  if request.method == 'GET':
    tutor_id = get_current_user().id  # get the current tutor id
    # get all lessons of the tutor
    lessons = Lesson.query.filter(Lesson.tutor_id == tutor_id).all()
    return render_template('tutor/create_schedule_existing_lesson.html', lessons=lessons)
  elif request.method == 'POST':
    tutor_id = get_current_user().id
    lessons = Lesson.query.filter(Lesson.tutor_id == tutor_id).all()
    existing_lesson_id = request.form.get('existing_lesson')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    print("i get", existing_lesson_id, start_time, end_time)
    if not (existing_lesson_id and start_time and end_time):  # if any of the fields are empty
      flash('Please fill in all fields.', 'danger')
    # Convert string to datetime objects
    start_datetime = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')

    # Perform validation checks
    if start_datetime < datetime.now():  # if start time is earlier than now
      flash("Start time must be later than now.", "danger")
    elif start_datetime >= end_datetime:  # if end time is earlier than start time
      flash("End time must be later than start time.", "danger")
    # if the schedule overlaps with the current schedule
    elif exist_overlap(start_datetime, end_datetime, tutor_id):
      flash("Intended schedule time overlaps with current schedule.", "danger")
    else:  # Save new schedule to the database
      schedule = Schedule(lesson_id=existing_lesson_id, tutor_id=tutor_id,
                          start_datetime=start_datetime, end_datetime=end_datetime, cost='100.00')
      db.session.add(schedule)
      db.session.commit()
      flash('Lesson schedule created successfully.', 'success')
      return redirect(url_for('tutor_view.manage_lesson_schedule'))
    return render_template('tutor/create_schedule_existing_lesson.html', lessons=lessons)


@tutor_view.route('/create_schedule_new_lesson', methods=['GET', 'POST'])
def create_schedule_new_lesson():

  if request.method == 'GET':  # if the page is loaded
    tutor_id = get_current_user().id
    lessons = Lesson.query.filter(Lesson.tutor_id == tutor_id).all()
    return render_template('tutor/create_schedule_new_lesson.html', lessons=lessons)
  elif request.method == 'POST':  # if the form is submitted
    tutor_id = get_current_user().id
    lessons = Lesson.query.filter(Lesson.tutor_id == tutor_id).all()
    lesson_title = request.form.get('lesson_title')
    lesson_number = request.form.get('lesson_number')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    cost = request.form.get('cost', type=float, default=100.00)
    description = request.form.get('description')
    print("i get", lesson_title, lesson_number, start_time, end_time)
    # if any of the fields are empty
    if not (lesson_title and lesson_number and start_time and end_time):
      flash('Please fill in all fields.', 'danger')
  # Convert string to datetime objects
    start_datetime = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
    # Perform validation checks
    if start_datetime < datetime.now():
      flash("Start time must be later than now.", "danger")
    elif start_datetime >= end_datetime:
      flash("End time must be later than start time.", "danger")
    elif exist_overlap(start_datetime, end_datetime, tutor_id):
      flash("Intended schedule time overlaps with current schedule.", "danger")
    else:
      # Save new lesson and new schedule to the database
      lesson = Lesson(title=lesson_title,
                      description=description,
                      lesson_number=lesson_number,
                      tutor_id=tutor_id,
                      cost=cost)
      db.session.add(lesson)
      db.session.commit()
      lesson_id = lesson.id
      schedule = Schedule(
          lesson_id=lesson_id, tutor_id=tutor_id, start_datetime=start_datetime, end_datetime=end_datetime)
      db.session.add(schedule)
      db.session.commit()
      flash('Lesson schedule created successfully.', 'success')
      return redirect(url_for('tutor_view.manage_lesson_schedule'))
    return render_template('tutor/create_schedule_new_lesson.html',
                           lessons=lessons,
                           lesson_title=lesson_title,
                           lesson_number=lesson_number,
                           start_time=start_time,
                           end_time=end_time,
                           cost=cost,
                           description=description)


@tutor_view.route('/<int:tutorid>/lessons', methods=['GET'])
@require_login()
def list_lesson(tutorid: int):
  page = request.args.get('page', 1, type=int)

  schedules = db.session.query(Schedule).filter(
      Schedule.tutor_id == tutorid,
      Schedule.lesson_id.isnot(None)
  ).order_by(
      Schedule.start_datetime.desc()
  ).paginate(page=page, per_page=10)

  now = datetime.now()

  return render_template('tutor/list_lesson.html',
                         schedules=schedules, tutor_id=tutorid, now=now)


@tutor_view.route('/<int:tutor_id>', methods=['GET'])
def view_tutor(tutor_id: int):
  tutor = db.session.query(User).get(tutor_id)
  return render_template('tutor/profile.html', member=tutor)


@tutor_view.route('/workshop_schedules', methods=['GET'])
def workshop_schedules():
  tutor = get_current_user()
  tutor_id = tutor.id
  filter = (Schedule.tutor_id == tutor_id) & (Schedule.workshop_id.isnot(None))
  search = request.args.get('search')
  page = request.args.get('page', 1, type=int)
  if search:
    filter = filter & (Workshop.title.ilike(f'%{search}%'))

  schedules = db.session.query(Schedule).filter(
      filter
  ).order_by(
      Schedule.start_datetime.desc()
  ).paginate(page=page, per_page=10)

  schedule_ids = [schedule.id for schedule in schedules]
  subquery = (
      db.session.query(
          Booking.schedule_id,
          func.count(Booking.id).label("total_bookings"),
          func.sum(case(
              (Booking.attended, 1), else_=0
          )).label("total_attended")
      )
      .group_by(Booking.schedule_id)
      .subquery()
  )

  schedules_counts = (
      db.session.query(
          Schedule.id,
          literal_column("0").label("total_bookings"),
          literal_column("0").label("total_attended")
      )
      .outerjoin(
          subquery,
          Schedule.id == subquery.c.schedule_id
      )
      .filter(filter & Schedule.id.in_(schedule_ids))
      .add_columns(
          subquery.c.total_bookings,
          subquery.c.total_attended
      )
      .all()
      # .from_self()
  )

  schedules_counts_dict = dict()
  for schedule in schedules_counts:
    schedules_counts_dict[schedule.id] = {
        'total_bookings': schedule.total_bookings,
        'total_attended': schedule.total_attended
    }

  return render_template('tutor/workshop_schedules.html', schedules=schedules, now=datetime.now(), search=search, schedules_counts_dict=schedules_counts_dict)


@ tutor_view.route('/workshop_schedules/new', methods=['GET'])
def create_workshop_schedule():

  return 'good'
