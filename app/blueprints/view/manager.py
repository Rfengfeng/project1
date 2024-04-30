from re import S
from sqlalchemy import func

from flask import Blueprint, flash, redirect, url_for, render_template, request
from sqlalchemy import or_
from app.models import User, Lesson, Schedule, Workshop, Booking, Reminder, Location, lesson, schedule
from app.models.booking import BookingStatus
from app.models.user import Role
from app.utils.attendance import get_booking_attendance
from app.utils.datetime import exist_overlap
from datetime import datetime, timedelta
from app.utils.hash import generate_password_hash, is_strong_password
from app.utils.session import get_current_user, require_login, require_roles
from app.utils.string_helper import generate_salt
from app.database import db
from app.models import User, Lesson, Schedule, Workshop, Booking, Reminder, News, Subscription, UserSubscription

from app.utils.datetime import exist_overlap


manager_view = Blueprint('manager_view', __name__)


@manager_view.before_request
def check_user():
  current_user = get_current_user()
  if not current_user or current_user.role != Role.manager.value:
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('user_view.login'))


@manager_view.route('/listmembers', methods=['GET', 'POST'])
def list_members():

  # Pagination settings
  page = request.args.get('page', 1, type=int)
  per_page = 12  # Number of members per page
  if request.method == 'POST':
    # Get the search query from the form
    search_query = request.form.get('query')
    # Perform a search query if it's not empty
    if search_query:
      search_term = f'%{search_query}%'
      members = db.session.query(User).filter(
          (User.role == Role.member.value) &
          (
              (User.first_name.ilike(search_term)) |
              (User.last_name.ilike(search_term)) |
              ((User.first_name + " " + User.last_name).ilike(search_term)) |
              (User.email.ilike(search_term))
          )
      ).paginate(page=page, per_page=per_page)
      if not members.items:
        flash("No result found.", "danger")
    else:
      # If search query is empty, just retrieve all tutors
      members = db.session.query(User).filter_by(
          role=Role.member.value).paginate(page=page, per_page=per_page)
  else:
    # If it's a GET request or no search query provided, retrieve all tutors
    members = db.session.query(User).filter_by(
        role=Role.member.value).paginate(page=page, per_page=per_page)
  return render_template('manager/list_members.html', members=members)


@manager_view.route('/listtutors', methods=['GET', 'POST'])
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
  return render_template('manager/list_tutors.html', tutors=tutors)


@manager_view.route('/addtutor', methods=['GET', 'POST'])
def add_tutor():
  if request.method == 'GET':
    return render_template('manager/add_tutor.html')
  elif request.method == 'POST':
    # Accessing form data directly
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    print(first_name, last_name, email, password, confirm_password)
    # Validate input fields
    all_filled = (
        first_name and last_name and email and password and confirm_password)
    if not all_filled:  # If any of the fields are empty
      flash("Please fill in all fields.", 'danger')
      return render_template('manager/add_tutor.html')
    elif db.session.query(User).filter_by(email=email).first():  # If email already exists
      flash('Email already registered.')
      return render_template('manager/add_tutor.html')
    elif not is_strong_password(password):  # If password is not strong
      flash('Password must be at least 8 characters long and have a mix of character types.', 'danger')
      return render_template('manager/add_tutor.html')
    elif password != confirm_password:  # If password and confirm password do not match
      flash('Password does not match confirm password.', 'danger')
      return render_template('manager/add_tutor.html')
    # Else create new user and commit to the database
    else:
      salt = generate_salt()
      password_hash = generate_password_hash(
          password, salt)  # Generate password hash
      user = User(first_name=first_name, last_name=last_name, email=email, role=Role.tutor.value, password=password_hash,
                  salt=salt, active=1)
      db.session.add(user)  # Add user to the database
      db.session.commit()
      flash("New tutor added.", 'danger')
      return redirect(url_for('manager_view.list_tutors'))


@manager_view.route('/addmember', methods=['GET', 'POST'])
def add_member():
  if request.method == 'GET':
    return render_template('manager/add_member.html')
  elif request.method == 'POST':
    # Accessing form data directly
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    # Validate input fields
    all_filled = first_name and last_name and email and password and confirm_password
    if not all_filled:  # If any of the fields are empty
      flash("Please fill in all fields.", 'danger')
      return render_template('manager/add_member.html')
    elif db.session.query(User).filter_by(email=email).first():  # If email already exists
      flash('Email already registered.')
      return render_template('manager/add_member.html')
    elif not is_strong_password(password):  # If password is not strong
      flash('Password must be at least 8 characters long and have a mix of character types.', 'danger')
      return render_template('manager/add_member.html')
    elif password != confirm_password:  # If password and confirm password do not match
      flash('Password does not match confirm password.', 'danger')
      return render_template('manager/add_tutor.html')
    # Else create new user and commit to the database
    else:
      salt = generate_salt()  # Generate salt
      password_hash = generate_password_hash(
          password, salt)  # Generate password hash
      user = User(first_name=first_name, last_name=last_name, email=email, role=Role.member.value, password=password_hash,
                  salt=salt, active=1)
      db.session.add(user)  # Add user to the database
      db.session.commit()  # Commit changes to the database
      flash("New member added.", 'danger')
      return redirect(url_for('manager_view.list_members'))


@manager_view.route('/manageprofile', methods=['GET', 'POST'])
def manage_profile():
  if request.method == 'GET':
    user_id = request.args.get('id')
    user = User.query.get_or_404(user_id)
    if not user:
      flash('User not found.', 'danger')
      return redirect(url_for('manager_view.dashboard'))  # Or a suitable page
    return render_template('manager/manage_profile.html', user=user)
  elif request.method == 'POST':
    # Access form data
    user_id = request.form.get('user_id')
    user = User.query.get(user_id)
    if not user:
      flash('User not found.', 'danger')
      return redirect(url_for('user_view.dashboard'))  # Or a suitable page

    # Update user profile
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    title = request.form.get('title')
    position = request.form.get('position')
    phone_number = request.form.get('phone_number')
    email = request.form.get('email')
    address = request.form.get('address')
    date_of_birth = request.form.get('date_of_birth')
    # Assuming 'active' is a boolean field
    active = request.form.get('active') == 'on'
    # requied_filled = first_name and last_name and email
    # if  not requied_filled:
    #   flash("Please fill in required fields: first name, last name, date of birth", 'danger')
    #   return render_template('user/manage_profile.html', user = user)
    user.first_name = first_name
    user.last_name = last_name
    user.title = title
    user.position = position
    user.phone_number = phone_number
    user.email = email
    user.address = address
    user.date_of_birth = date_of_birth
    user.active = active
    db.session.merge(user)  # Merge the user object into the session
    db.session.commit()  # Commit the changes to the database
    flash("Profile updated successfully.", 'success')
    # Redirect to the appropriate page based on the user's role
    if user.role == Role.member.value:
      return redirect(url_for('manager_view.list_members'))
    if user.role == Role.tutor.value:
      return redirect(url_for('manager_view.list_tutors'))
  return render_template('manager/manage_profile.html', user=user)


@manager_view.route('/list_workshop', methods=['GET', 'POST'])
@require_login()
def list_workshop():
  workshops = db.session.query(Workshop).all()
  # Get the current logged-in user
  current_user = get_current_user()
  # Get the current datetime
  current_datetime = datetime.now()
 # Get the week offset from the request query parameter
  week_offset = int(request.args.get('week_offset', 0))
  # Calculate the start and end of the current week based on the week offset
  start_of_week = current_datetime - \
      timedelta(days=current_datetime.weekday()) + timedelta(weeks=week_offset)
  end_of_week = start_of_week + timedelta(days=6)
# Initialize variables for selected workshop ID and schedules
  selected_workshop_id = ""
  if request.method == 'GET':
      # If it's a GET request, retrieve schedules for the current week
    schedules = db.session.query(Schedule).filter(
        Schedule.workshop_id.isnot(None),
        Schedule.start_datetime >= start_of_week,
        Schedule.start_datetime <= end_of_week
    ).all()
  if request.method == 'POST':
   # If it's a POST request, handle the form submission
    selected_workshop_id = request.form.get('workshopFilter')
    week_offset = int(request.form.get('week_offset', 0)) or week_offset
    # Recalculate start and end of the week based on the updated week offset
    start_of_week = current_datetime - \
        timedelta(days=current_datetime.weekday()) + \
        timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    if selected_workshop_id == "":
      # Filter schedules by workshop ID if a workshop is selected
      schedules = db.session.query(Schedule).filter(
          Schedule.workshop_id.isnot(None),
          Schedule.start_datetime >= start_of_week,
          Schedule.start_datetime <= end_of_week
      ).all()
    else:  # Filter schedules by selected workshop ID
      schedules = db.session.query(Schedule).filter(
          Schedule.workshop_id == selected_workshop_id,
          Schedule.start_datetime >= start_of_week,
          Schedule.start_datetime <= end_of_week
      ).all()
      # Group schedules by day of the week
  grouped_schedules = {}
  if not schedules:
    flash('No workshop schedules found.', 'danger')

  else:
    for schedule in schedules:
      day_of_week = schedule.start_datetime.strftime('%A')
      if day_of_week not in grouped_schedules:
        grouped_schedules[day_of_week] = []
      grouped_schedules[day_of_week].append(schedule)

    # Format date strings for current week start and end
  current_week_start = start_of_week.strftime('%Y-%m-%d')
  current_week_end = end_of_week.strftime('%Y-%m-%d')
  now = datetime.now()
  # Render the HTML template with the retrieved data
  return render_template('manager/list_workshop.html', grouped_schedules=grouped_schedules,
                         current_user=current_user, current_datetime=current_datetime,
                         week_offset=week_offset, workshops=workshops,
                         current_week_start=current_week_start,
                         current_week_end=current_week_end,
                         selected_workshop_id=selected_workshop_id,
                         now=now)


@manager_view.route('/edit_workshop_schedule/<int:id>', methods=['GET', 'POST'])
@require_login()
def edit_workshop_schedule(id: int):
    # Retrieve all tutors from the database
  tutors = db.session.query(User).filter(
      User.role == 'tutor'
  ).all()
  if request.method == 'GET':
   # Handle GET request to display the form for editing the schedule

      # Retrieve the current schedule with the specified id
    current_schedule = db.session.query(Schedule).filter(
        Schedule.id == id
    ).first()
    if not current_schedule:

       # If schedule with the given id is not found, show an error and redirect
      flash('Schedule not found.', 'danger')
      return redirect(url_for('manager_view.list_workshop'))

    # Render the HTML template with the retrieved data
    return render_template('manager/edit_workshop_schedule.html',
                           schedule=current_schedule,
                           tutors=tutors,
                           tutor_id=current_schedule.tutor_id
                           )

  elif request.method == 'POST':
    # Handle POST request to update the schedule
     # Retrieve the current schedule with the specified id
    current_schedule = db.session.query(Schedule).filter(
        Schedule.id == id
    ).first()

    if not current_schedule:
     # If schedule with the given id is not found, show an error and redirect
      flash('Schedule not found.', 'danger')
      return redirect(url_for('manager_view.list_workshop'))

    # Update workshop schedule
    workshop_id = request.form.get('workshop_id')
    workshop = db.session.query(Workshop).get(workshop_id)
    start_datetime = datetime.strptime(
        request.form.get('start_datetime'), '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(
        request.form.get('end_datetime'), '%Y-%m-%dT%H:%M')
    tutor_id = request.form.get('tutor_id')

    error = ''
    if start_datetime < datetime.now():
      error = "Start time must be later than now."
    elif start_datetime >= end_datetime:
      error = "End time must be later than start time."
    elif exist_overlap(start_datetime, end_datetime, tutor_id, location_id=workshop.location_id, current_schedule_id=current_schedule.id):
      error = "Intended schedule time overlaps with current schedule."
    if error:
      flash(error, 'danger')
      return render_template('manager/edit_workshop_schedule.html',
                             schedule=current_schedule,
                             tutors=tutors,
                             tutor_id=int(tutor_id),
                             start_datetime=start_datetime,
                             end_datetime=end_datetime,
                             )

    # update schedule into database
    current_schedule.workshop_id = workshop_id
    current_schedule.start_datetime = start_datetime
    current_schedule.end_datetime = end_datetime
    current_schedule.tutor_id = tutor_id

   # Commit the changes to the database
    db.session.merge(current_schedule)
    db.session.commit()
   # Show success message and redirect to the list_workshop route
    flash("Workshop schedule updated successfully.", 'success')
    return redirect(url_for('manager_view.list_workshop'))


@manager_view.route('/delete_workshop_schedule/<int:id>', methods=['GET', 'POST'])
@require_login()
def delete_workshop_schedule(id: int):
 # Retrieve the current schedule with the specified id
  current_schedule = db.session.query(Schedule).filter(
      Schedule.id == id
  ).first()
  if not current_schedule:
    # If schedule with the given id is not found, show an error flash message
    flash('Schedule not found.', 'danger')
  # If schedule is found, delete it from the database
  db.session.delete(current_schedule)
  db.session.commit()
  flash("Workshop Scheduel deleted successfully.", 'success')
  # Redirect the user to the list_workshop route after deletion
  return redirect(url_for('manager_view.list_workshop'))


@manager_view.route('/add_workshop_schedule', methods=['GET', 'POST'])
def add_workshop_schedule():
  workshops = db.session.query(Workshop).all()
  tutors = db.session.query(User).filter(
      User.role == 'tutor'
  ).all()
  if request.method == 'GET':
     # Handle GET request to display the form for adding a new workshop schedule
    return render_template('manager/add_workshop_schedule.html', workshops=workshops, tutors=tutors)

  if request.method == 'POST':
    # Handle POST request to add a new workshop schedule

    # Retrieve form data for creating the new schedule
    workshop_id = request.form.get('workshop_id')
    start_datetime = datetime.strptime(
        request.form.get('start_datetime'), '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(
        request.form.get('end_datetime'), '%Y-%m-%dT%H:%M')
    tutor_id = request.form.get('tutor_id')

    # Retrieve the workshop and tutor objects based on the provided IDs
    workshop = db.session.query(Workshop).filter_by(
        id=workshop_id).first()
    tutor = db.session.query(User).filter_by(
        id=tutor_id).first()

    if not workshop or not tutor:  # Check if the workshop or tutor is not found
      flash("Workshop or tutor not found.", 'error')
      return redirect(url_for('manager_view.add_workshop_schedule'))

    error = ''
    if start_datetime < datetime.now():
      error = "Start time must be later than now."
    elif start_datetime >= end_datetime:
      error = "End time must be later than start time."
    elif exist_overlap(start_datetime, end_datetime, tutor_id, location_id=workshop.location_id):
      error = "Intended schedule time overlaps with current schedule."
    if error:
      flash(error, 'danger')
      return render_template('manager/add_workshop_schedule.html',
                             workshops=workshops,
                             workshop_id=workshop_id,
                             tutors=tutors,
                             tutor_id=int(tutor_id),
                             start_datetime=start_datetime,
                             end_datetime=end_datetime
                             )

     # Create a new schedule object and add it to the database
    new_schedule = Schedule(
        workshop_id=workshop.id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        tutor_id=tutor_id,
        cost=workshop.price
    )

    db.session.add(new_schedule)
    db.session.commit()
 # Show success flash message after successfully adding the schedule
    flash("Workshop Scheduel Added successfully.", 'success')
    return redirect(url_for('manager_view.list_workshop'))


@manager_view.route('/add_lesson', methods=['GET', 'POST'])
def add_lesson():

  if request.method == 'GET':
    tutors = db.session.query(User).filter(
        User.role == Role.tutor.value).all()
    return render_template('manager/add_lesson.html', tutors=tutors)

  if request.method == 'POST':
    # handle form submission
    title = request.form.get('lesson_title')
    tutor_id = request.form.get('tutor')
    cost = request.form.get('lesson_cost')
    lesson_number = request.form.get('lesson_number')
    lesson_description = request.form.get('lesson_description')

    if not (title and tutor_id and cost and lesson_number):  # If any of the fields are empty
      flash('Please fill in all fields.', 'danger')
      return render_template('manager/add_lesson.html', tutors=tutors)

    if not cost.replace('.', '', 1).isdigit():  # If cost is not a number
      flash('Cost must be a number.', 'danger')
      return render_template('manager/add_lesson.html', tutors=tutors)

    if title in [lesson.title for lesson in Lesson.query.all()]:  # If lesson title already exists
      flash('Lesson title already exists.', 'danger')
      return render_template('manager/add_lesson.html', tutors=tutors)

    # If lesson number already exists
    if lesson_number in [lesson.lesson_number for lesson in Lesson.query.all()]:
      flash('Lesson number already exists.', 'danger')
      return render_template('manager/add_lesson.html', tutors=tutors)

    # Create a new lesson record in the database
    lesson = Lesson(
        title=title,
        tutor_id=tutor_id,
        cost=cost,
        lesson_number=lesson_number,
        description=lesson_description
    )
    db.session.add(lesson)  # Add lesson to the database
    db.session.commit()  # Commit the changes to the database
    return redirect(url_for('manager_view.list_lessons_get'))


@manager_view.route('/list_lessons', methods=['GET'])
def list_lessons_get():
  page = request.args.get('page', 1, type=int)
  per_page = 10  # Number of lessons per page
  lessons = db.session.query(Lesson).paginate(
      page=page, per_page=per_page)
  tutors = db.session.query(User).filter_by(
      role=Role.tutor.value).all()
  return render_template('manager/list_lessons.html', lessons=lessons, tutors=tutors)


@manager_view.route('/list_lessons', methods=['POST'])
def list_lessons_post():
    # Check if the request method is POST
  if request.method == 'POST':
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of lessons per page
    search_query = request.form.get('search')
    tutor_id = request.form.get('tutor')

    # Initialize lessons query
    lessons_query = Lesson.query

    # Perform a search query if a search query is provided
    if search_query:
      lessons_query = lessons_query.filter(
          (Lesson.title.ilike(f'%{search_query}%')) |
          (Lesson.lesson_number.ilike(f'%{search_query}%'))
      )

    # Filter by tutor if a tutor is selected
    if tutor_id:
      lessons_query = lessons_query.filter_by(tutor_id=tutor_id)

    # Paginate the results
    lessons = lessons_query.paginate(page=page, per_page=per_page)

    # Get all tutors for the dropdown list
    tutors = User.query.filter_by(role=Role.tutor.value).all()

    if not lessons.items:
      flash("No result found.", "danger")

    # Render the template with the search results or all lessons
    return render_template('manager/list_lessons.html', lessons=lessons, tutors=tutors)


@manager_view.route('view_lesson/<int:id>', methods=['GET'])
def view_lesson(id):
  # Get the lesson with the specified id
  lesson = db.session.query(Lesson).get(id)
  if not lesson:
    flash('Lesson not found', 'danger')
    return redirect(url_for('manager_view.list_lessons_get'))
  return render_template('manager/view_lesson.html', lesson=lesson)


@manager_view.route('/edit_lesson/<int:lesson_id>', methods=['POST'])
def edit_lesson_post(lesson_id):
  lesson = Lesson.query.get(lesson_id)
  if lesson is None:
    flash('Lesson not found.', 'error')
    return redirect(url_for('manager_view.list_lessons_get'))
  # handle form submission
  title = request.form.get('lesson_title')
  tutor_id = request.form.get('tutor')
  cost = request.form.get('lesson_cost')
  lesson_number = request.form.get('lesson_number')
  lesson_description = request.form.get('lesson_description')
  # Perform validation checks on the input fields
  if not (title and tutor_id and cost and lesson_number):
    flash('Please fill in all fields.', 'danger')
    return redirect(url_for('manager_view.edit_lesson_get', lesson_id=lesson_id))
  # Check if cost is a number
  if not cost.replace('.', '', 1).isdigit():
    flash('Cost must be a number.', 'danger')
    return redirect(url_for('manager_view.edit_lesson_get', lesson_id=lesson_id))
  # Check if title and lesson number already exist
  if (title != lesson.title) and (title in [lesson.title for lesson in Lesson.query.all()]):
    flash('Lesson title already exists.', 'danger')
    return redirect(url_for('manager_view.edit_lesson_get', lesson_id=lesson_id))
  # Check if lesson number already exists
  if (lesson_number != lesson.lesson_number) and (lesson_number in [lesson.lesson_number for lesson in Lesson.query.all()]):
    flash('Lesson number already exists.', 'danger')
    return redirect(url_for('manager_view.edit_lesson_get', lesson_id=lesson_id))
  # Update the lesson record in the database
  lesson.title = title
  lesson.tutor_id = tutor_id
  lesson.cost = cost
  lesson.lesson_number = lesson_number
  lesson.description = lesson_description
  db.session.commit()  # Commit the changes to the database

  flash('Lesson updated successfully.', 'success')
  return redirect(url_for('manager_view.list_lessons_get'))


@manager_view.route('/edit_lesson/<int:lesson_id>', methods=['GET'])
def edit_lesson_get(lesson_id):
  # If the request method is GET, render the template for editing the lesson
  if request.method == 'GET':
    # Get the lesson with the specified id
    lesson = Lesson.query.get(lesson_id)
    tutors = db.session.query(User).filter_by(
        role=Role.tutor.value).all()
    if lesson is None:
      flash('Lesson not found.', 'error')
      return redirect(url_for('manager_view.list_lessons_get'))
    return render_template('manager/edit_lesson.html', lesson=lesson, tutors=tutors)


@manager_view.route('/manager/delete_lesson/<int:lesson_id>', methods=['POST'])
def delete_lesson(lesson_id):
  lesson = Lesson.query.get(lesson_id)
  if lesson:
    if lesson.schedules:
      flash('A scheduled lesson cannot be deleted', 'danger')
      return redirect(url_for('manager_view.list_lessons_get'))
    # Delete the lesson record from the database
    db.session.delete(lesson)
    db.session.commit()
    flash('Lesson deleted successfully.', 'success')
  else:
    flash('Lesson not found.', 'error')
  return redirect(url_for('manager_view.list_lessons_get'))


@manager_view.route('/manager/list_schedules/<int:lesson_id>', methods=['GET'])
def list_schedules(lesson_id):
  lesson = Lesson.query.get(lesson_id)
  if not lesson:
    flash('Lesson not found.', 'error')
    return redirect(url_for('manager_view.list_lessons_get'))
  # Pagination settings
  page = request.args.get('page', 1, type=int)
  per_page = 10  # Adjust as needed
  # Get all schedules for the lesson
  schedules = Schedule.query.filter_by(
      lesson_id=lesson_id).order_by(
      Schedule.start_datetime.desc()
  ).paginate(page=page, per_page=per_page)

  return render_template('manager/list_schedules.html', lesson=lesson, schedules=schedules, now=datetime.now())


@manager_view.route('/add_schedule/<int:lesson_id>', methods=['GET', 'POST'])
def add_schedule(lesson_id):
  if request.method == 'POST':
    # handle form submission
    tutor_id = request.form.get('tutor')
    start_datetime = request.form.get('start_datetime')
    end_datetime = request.form.get('end_datetime')
    lesson = Lesson.query.get(lesson_id)
    # Perform validation checks
    if not (tutor_id and start_datetime and end_datetime):
      flash('Please fill in all fields.', 'danger')
      return redirect(url_for('manager_view.add_schedule', lesson_id=lesson_id))

    start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
    end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')
    # Perform validation checks
    if start_datetime < datetime.now():  # If start time is earlier than now
      flash("Start time must be later than now.", "danger")
      return redirect(url_for('manager_view.add_schedule', lesson_id=lesson_id))

    elif start_datetime >= end_datetime:  # If end time is earlier than start time
      flash("End time must be later than start time.", "danger")
      return redirect(url_for('manager_view.add_schedule', lesson_id=lesson_id))

    elif exist_overlap(start_datetime, end_datetime, tutor_id):  # If there is an overlap
      flash("Intended schedule time overlaps with current schedule.", "danger")
      return redirect(url_for('manager_view.add_schedule', lesson_id=lesson_id))

    else:  # Add the schedule to the database
      schedule = Schedule(
          lesson_id=lesson_id,
          tutor_id=tutor_id,
          start_datetime=start_datetime,
          end_datetime=end_datetime,
          cost=lesson.cost
      )
      db.session.add(schedule)
      db.session.commit()
      flash('Schedule added successfully.', 'success')
      return redirect(url_for('manager_view.list_schedules', lesson_id=lesson_id))

  if request.method == 'GET':
    tutors = db.session.query(User).filter(
        User.role == Role.tutor.value).all()
    return render_template('manager/add_schedule.html', lesson_id=lesson_id, tutors=tutors)


@manager_view.route('/manager/delete_schedule/<int:schedule_id>', methods=['POST'])
def delete_schedule(schedule_id):

  # Get the schedule with the specified id
  schedule = Schedule.query.get(schedule_id)

  if schedule:
    if db.session.query(Booking).filter(
        (Booking.schedule_id == schedule_id) &
        (Booking.status == BookingStatus.confirmed.value)
    ).first():  # If there are confirmed bookings
      flash('Cannot delete schedule with confirmed bookings.', 'error')
      return redirect(url_for('manager_view.list_lessons_get'))
    # Delete the schedule record from the database
    lesson_id = schedule.lesson.id
    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully.', 'success')
    return redirect(url_for('manager_view.list_schedules', lesson_id=lesson_id))

  else:  # If the schedule is not found
    flash('Schedule not found.', 'error')
    return redirect(url_for('manager_view.list_lessons_get'))


@manager_view.route('/manager/edit_schedule/<int:schedule_id>', methods=['GET'])
def edit_schedule_get(schedule_id):

  schedule = Schedule.query.get(schedule_id)

  if not schedule:
    flash('Schedule not found.', 'error')
    return redirect(url_for('manager_view.list_lessons_get'))
  tutors = db.session.query(User).filter_by(
      role=Role.tutor.value).all()  # Get all tutors

  return render_template('manager/edit_schedule.html', schedule=schedule, tutors=tutors)


@manager_view.route('/edit_schedule/<int:schedule_id>', methods=['POST'])
def edit_schedule_post(schedule_id):
  if request.method == 'POST':
    tutor_id = request.form.get('tutor')
    start_datetime = request.form.get('start_datetime')
    end_datetime = request.form.get('end_datetime')

  if not (tutor_id and start_datetime and end_datetime):
    flash('Please fill in all fields.', 'danger')
    return redirect(url_for('manager_view.edit_schedule_get', schedule_id=schedule_id))

  start_datetime = datetime.strptime(start_datetime, '%Y-%m-%dT%H:%M')
  end_datetime = datetime.strptime(end_datetime, '%Y-%m-%dT%H:%M')
  # Perform validation checks
  if start_datetime < datetime.now():
    flash("Start time must be later than now.", "danger")
    return redirect(url_for('manager_view.edit_schedule_get', schedule_id=schedule_id))

  elif start_datetime >= end_datetime:
    flash("End time must be later than start time.", "danger")
    return redirect(url_for('manager_view.edit_schedule_get', schedule_id=schedule_id))

  elif exist_overlap(start_datetime, end_datetime, tutor_id):
    flash("Intended schedule time overlaps with current schedule.", "danger")
    return redirect(url_for('manager_view.edit_schedule_get', schedule_id=schedule_id))

  else:
    # Update the start and end datetimes of the current schedule
    schedule = Schedule.query.get(schedule_id)
    schedule.start_datetime = start_datetime
    schedule.end_datetime = end_datetime

    db.session.merge(schedule)
    db.session.commit()

    flash('Changes have been saved.', 'success')
    lesson_id = schedule.lesson.id
    return redirect(url_for('manager_view.list_lessons_get'))


@manager_view.route('/manage_workshop_list', methods=['GET', 'POST'])
@require_login()
def manage_workshop_list():
   # Get the current page number from the request (default to 1 if not provided)
  page = request.args.get('page', 1, type=int)
  query = db.session.query(Workshop)

 # Retrieve workshops, ordered by title in descending order, and paginate the results
  workshops = query.order_by(
      Workshop.title.desc()
  ).paginate(page=page, per_page=10)

  # Get the current logged-in user
  current_user = get_current_user()

  return render_template('manager/manage_workshop_list.html',
                         current_user=current_user,  workshops=workshops
                         )


@manager_view.route('/edit_workshop_list/<int:workshop_id>', methods=['GET'])
def edit_workshop_list(workshop_id):
   # Print out the workshop_id for debugging purposes
  print(workshop_id)
  # Retrieve the workshop with the specified workshop_id from the database
  workshop = db.session.query(Workshop).filter_by(
      id=int(workshop_id)).first()

  # Retrieve the current logged-in user
  current_user = get_current_user()

  # Retrieve all locations from the database
  locations = db.session.query(Location).all()

  return render_template('manager/edit_workshop_list.html',
                         current_user=current_user,  workshop=workshop, locations=locations
                         )


@manager_view.route('/edit_workshop_list/<int:workshop_id>', methods=['POST'])
def edit_workshop_db(workshop_id):

  workshop_id = request.form.get('workshop_id')
  workshop_name = request.form.get('workshop_name')
  location_id = request.form.get('location_id')
  workshop_description = request.form.get('workshop_description')
  price = request.form.get('price', type=float, default=0.0)
  # Retrieve the workshop object based on the provided workshop_id
  workshop = Workshop.query.get(workshop_id)

  if workshop:
    # Update the workshop details with the submitted form data
    workshop.title = workshop_name
    workshop.location_id = location_id
    workshop.description = workshop_description
    workshop.price = price
  # Merge the updated workshop object into the session and commit the changes
    db.session.merge(workshop)
    db.session.commit()

    flash('Workshop updated successfully!', 'success')
  else:
    flash('Workshop not found!', 'error')

  return redirect(url_for('manager_view.manage_workshop_list'))


@manager_view.route('/manager/delete_workshop/<int:workshop_id>', methods=['POST'])
def delete_workshop(workshop_id):
  # Retrieve the workshop object based on the provided workshop_id
  workshop = Workshop.query.get(workshop_id)
  if workshop:
     # If the workshop object exists, delete it from the database
    db.session.delete(workshop)
    db.session.commit()
    # Display a success flash message after successfully deleting the workshop
    flash('Workshop deleted successfully.', 'success')
  else:
    # If the workshop with the specified id is not found, display an error flash message
    flash('Workshop not found.', 'error')
  return redirect(url_for('manager_view.manage_workshop_list'))


@manager_view.route('/add_workshop', methods=['GET'])
@require_login()
def add_workshop():
  # Retrieve all locations from the database
  locations = db.session.query(Location).all()
  # Retrieve the current logged-in user
  current_user = get_current_user()

  # Render the 'manager/add_workshop.html' template with the retrieved data
  return render_template('manager/add_workshop.html', current_user=current_user, locations=locations)


@manager_view.route('/add_workshop', methods=['POST'])
@require_login()
def add_workshop_db():
   # Retrieve form data for adding a new workshop
  workshop_name = request.form.get('workshop_name')
  location_id = request.form.get('location_id')
  description = request.form.get('workshop_description')
  price = request.form.get('price', type=float, default=0.0)
 # Create a new Workshop object with the retrieved form data
  new_workshop = Workshop(
      title=workshop_name,
      location_id=location_id,
      description=description,
      price=price,
  )
  # Add the new workshop object to the session and commit the changes to the database
  db.session.add(new_workshop)
  db.session.commit()
  # Display a success flash message after successfully adding the new workshop
  flash('Workshop added successfully!', 'success')
  # Redirect the user back to the manage_workshop_list route
  return redirect(url_for('manager_view.manage_workshop_list'))


@manager_view.route('/view_workshop_description/<int:workshop_id>', methods=['GET'])
@require_login()
def view_workshop_description(workshop_id):
  # Retrieve the current logged-in user
  current_user = get_current_user()

  # Retrieve the workshop object based on the provided workshop_id from the database
  workshop = db.session.query(Workshop).filter_by(id=workshop_id).first()
  # Render the 'manager/view_workshop_description.html' template with the retrieved data
  return render_template('manager/view_workshop_description.html', current_user=current_user, workshop=workshop)


@manager_view.route('/workshop_search', methods=['GET'])
def workshop_search():
  # Retrieve the 'query' parameter from the request's query string
  query = request.args.get('query')
  # if input nothing
  if query == '':
    flash("Please input a name for search", 'danger')
    return redirect(url_for('manager_view.manage_workshop_list'))
  # Retrieve the 'page' parameter from the request's query string
  page = request.args.get('page', 1, type=int)

  # Define the number of workshops to display per page
  per_page = 10
  # Query the database for workshops that match the search query (case-insensitive)
  workshops = db.session.query(Workshop).filter(
      func.lower(Workshop.title).ilike(f'%{query.lower()}%')
  ).paginate(page=page, per_page=per_page)
  # If no workshops are found, display a flash message and redirect to the manage_workshop_list route
  if not workshops:
    flash("Can't find any workshop matches", 'danger')
    return redirect(url_for('manager_view.manage_workshop_list'))
  else:
    flash("Workshops found", 'success')
  return render_template('manager/manage_workshop_list.html', workshops=workshops)


@manager_view.route('/member_attendance/<int:member_id>')
@require_login()
def member_attendance(member_id):
    # Query for the member's information
  member = User.query.filter_by(id=member_id).first()
  lesson_page = request.args.get('lesson_page', 1, type=int)
  workshop_page = request.args.get('workshop_page', 1, type=int)
  if not member:
    flash("Member not found.", "danger")
    return redirect(url_for('manager_view.list_members'))

  # Combine query for lessons and workshops with attendance status
  lesson_bookings = Booking.query.join(Schedule).join(Lesson).filter(
      Booking.user_id == member_id,
      Schedule.lesson_id.isnot(None),
      Booking.start_datetime < datetime.now()
  ).paginate(page=lesson_page, per_page=10)

  workshop_bookings = Booking.query.join(Schedule).join(Workshop).filter(
      Booking.user_id == member_id,
      Schedule.workshop_id.isnot(None),
      Booking.start_datetime < datetime.now()
  ).paginate(page=workshop_page, per_page=10)

  return render_template('manager/member_attendance.html',
                         member=member,
                         lesson_bookings=lesson_bookings,
                         workshop_bookings=workshop_bookings,
                         lesson_page=lesson_page,
                         workshop_page=workshop_page
                         )


@manager_view.route('/locations', methods=['GET'])
def list_locations():
  page = request.args.get('page', 1, type=int)
  search_string = request.args.get('search_string', '')

  query = db.session.query(Location)
  if search_string:
    query = query.filter(
        or_(
            Location.title.ilike(f'%{search_string}%'),
            Location.city.ilike(f'%{search_string}%'),
            Location.state.ilike(f'%{search_string}%')
        )
    )
  location_list = query.order_by(
      Location.title
  ).paginate(page=page, per_page=10)

  return render_template('manager/locations_list.html', location_list=location_list)


@manager_view.route('/news', methods=['GET'])
def list_news():
  page = request.args.get('page', 1, type=int)
  search_string = request.args.get('search_string', '')

  query = db.session.query(News)
  if search_string:
    query = query.filter(
        News.title.ilike(f'%{search_string}%')
    )
  news = query.order_by(
      News.published_at.desc()
  ).paginate(page=page, per_page=10)

  return render_template('manager/news_list.html', news_list=news)


@manager_view.route('/user/<int:id>', methods=['GET'])
@require_roles([Role.manager, Role.tutor])
def view_profile(id: int):
  user = db.session.query(User).get(id)
  if not user:
    flash('User not found', 'danger')
    return redirect(url_for('user_view.list_users'))
  (lessons_booked, lessons_attended,
   lesson_bookings) = get_booking_attendance(user, 'lesson')
  (workshops_booked, workshops_attended,
   workshop_bookings) = get_booking_attendance(user, 'workshop')

  return render_template('manager/user_profile.html',
                         user=user,
                         page_title='User Profile ' + user.full_name,
                         now=datetime.now(),
                         lessons_booked=lessons_booked, lessons_attended=lessons_attended, lesson_bookings=lesson_bookings,
                         workshops_booked=workshops_booked, workshops_attended=workshops_attended, workshop_bookings=workshop_bookings)


@manager_view.route('/list_subscriptions', methods=['GET'])
def list_subscriptions():
  page = request.args.get('page', 1, type=int)
  per_page = 10  # Number of subscriptions per page
  subscriptions = Subscription.query.paginate(page=page, per_page=per_page)
  return render_template('manager/list_subscriptions.html', subscriptions=subscriptions)


@manager_view.route('/add_subscription', methods=['GET', 'POST'])
def add_subscription():
  if request.method == 'GET':
    return render_template('subscriptions/add_subscription.html')

  if request.method == 'POST':
    title = request.form.get('title')
    price = request.form.get('price')
    duration = request.form.get('duration')
    description = request.form.get('description')

    if not (title and price and duration):
      flash('Please fill in all required fields.', 'danger')
      return render_template('subscriptions/add_subscription.html')

    # Validate numeric fields
    try:
      price = float(price)
      duration = int(duration)
    except ValueError:
      flash('Invalid data for price or duration.', 'danger')
      return render_template('subscriptions/add_subscription.html')

    new_subscription = Subscription(
        title=title, price=price, duration=duration, description=description)
    db.session.add(new_subscription)
    db.session.commit()
    flash('Subscription added successfully.', 'success')
    return redirect(url_for('manager_view.list_subscriptions'))


@manager_view.route('/edit_subscription/<int:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
  subscription = Subscription.query.get_or_404(subscription_id)
  if request.method == 'GET':
    return render_template('subscriptions/edit_subscription.html', subscription=subscription)

  if request.method == 'POST':
    subscription.title = request.form.get('title')
    subscription.description = request.form.get('description')
    subscription.price = float(request.form.get('price'))
    subscription.duration = int(request.form.get('duration'))

    db.session.commit()
    flash('Subscription updated successfully.', 'success')
    return redirect(url_for('manager_view.list_subscriptions'))


@manager_view.route('/delete_subscription/<int:subscription_id>', methods=['POST'])
def delete_subscription(subscription_id):
    # Check if the subscription is in use
  user_subscription_exists = UserSubscription.query.filter_by(
      subscription_id=subscription_id).first()

  # If the subscription is in use, prevent deletion
  if user_subscription_exists:
    flash('This subscription cannot be deleted because it is currently in use.', 'danger')
    return redirect(url_for('manager_view.list_subscriptions'))

  # Otherwise, delete the subscription
  subscription = Subscription.query.get(subscription_id)
  if subscription:
    db.session.delete(subscription)
    db.session.commit()
    flash('Subscription deleted successfully.', 'success')
  else:
    flash('Subscription not found.', 'danger')

  return redirect(url_for('manager_view.list_subscriptions'))
