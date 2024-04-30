from flask import request
from sqlalchemy import func
from datetime import datetime, timedelta, date
from flask import (
    Blueprint, request, render_template, flash, session, redirect, url_for,
)

from app.models import User, Schedule, Workshop, UserSubscription
from app.database import db
from app.models.booking import Booking, BookingStatus
from app.models.lesson import Lesson
from app.models.news import News
from app.models.reminder import Reminder
from app.models.user import Role
from app.utils.reminder import create_subscription_reminder
from app.utils.session import get_current_user, require_login, require_roles, set_current_user
from app.forms import EditProfileForm
from app.utils.string_helper import generate_salt, get_greeting
from app.utils.hash import generate_password_hash, is_strong_password
from app.utils.timetable import build_time_table, build_time_table_of_this_month

user_view = Blueprint('user_view', __name__)


@user_view.route('/login', methods=['GET', 'POST'])
def login():
  email = ''
  if request.method == 'POST':
    email = request.form.get('email', '').strip()
    password = request.form.get('password')

    # user = User.query.filter_by(email=email).first()
    user = db.session.query(User).filter_by(email=email).first()

    if user is None or not generate_password_hash(password, user.salt) == user.password:
      flash('Incorrect email or password.', 'danger')
    else:
      if not user.active:
        flash('Your account is disabled. Please contact the administrator.', 'danger')
        return redirect(url_for('user_view.login'))

      set_current_user(user)

      if user.role == Role.member.value:
        create_subscription_reminder(user)
        db.session.commit()

      flash('Login successful! Welcome!', 'success')

      redirect_url = request.args.get('next') or url_for('user_view.dashboard')
      return redirect(redirect_url)

  return render_template('user/login.html', email=email)


@user_view.route('/register', methods=['GET', 'POST'])
def register():
  if request.method == 'POST':
    error = None
    # Retrieve data from the form
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    title = request.form.get('title')
    position = request.form.get('position')
    phone_number = request.form.get('phone_number')
    address = request.form.get('address')
    date_of_birth = request.form.get('date_of_birth')

    # Validate input fields
    if not first_name:
      error = 'First name is required!'
    elif not last_name:
      error = 'Last name is required.'
    elif not password:
      error = 'Password is required.'
    elif password != confirm_password:
      error = 'Passwords must match.'
    elif not title:
      error = 'Title cannot be empty.'
    elif not phone_number:
      error = 'Phone number is required.'
    elif not address:
      error = 'Address is required.'
    elif not date_of_birth:
      error = 'Date of birth is required.'
    elif db.session.query(User).filter_by(email=email).first():
      error = 'Email already registered.'
    elif not is_strong_password(password):
      error = 'Password must be at least 8 characters long and have a mix of character types.'

    # Validate phone number format after all other fields have been validated
    if not error:
      import re
      phone_pattern = re.compile(r'(?:0|\+)[0-9]{4,20}')
      if not phone_pattern.match(phone_number):
        error = 'Invalid phone number format. Please enter a valid phone number.'

    # Parse date of birth from the form and validate age
    try:
      date_of_birth = datetime.strptime(request.form.get(
          'date_of_birth'), '%Y-%m-%d')
      eighteen_years_ago = datetime.now() - timedelta(days=18*365.25)
      if date_of_birth > eighteen_years_ago:
        error = 'You must be at least 18 years old to register.'
    except ValueError as e:
      error = 'Invalid date of birth format.'

    # Display error message if there is an error
    if error:
      flash(error, 'danger')
      return render_template('user/register.html', **locals())

    # Create new user and commit to the database
    salt = generate_salt()
    password_hash = generate_password_hash(password, salt)
    user = User(first_name=first_name, last_name=last_name, email=email, title=title, date_of_birth=date_of_birth, position=position,
                address=address, phone_number=phone_number, role=Role.member.value, password=password_hash, salt=salt, active=1)
    db.session.add(user)
    db.session.flush()

    reminder = Reminder.create_welcome_message(user.id)
    db.session.add(reminder)

    db.session.commit()
    set_current_user(user)

    # Registration successful, redirect to login page
    flash('Registration successful! Please choose your plan.', 'success')
    return redirect(url_for('subscription_view.pricing', user_id=user.id))

  # Handle GET request, show registration form
  return render_template('user/register.html')


@user_view.route('/dashboard', methods=['GET'])
@require_login()
def dashboard():
  user = get_current_user()
  greeting = get_greeting()
  reminder_count = db.session.query(Reminder).filter(
      (Reminder.receiver_id == user.id) & (Reminder.read_at == None)).count()

  if user.role == Role.member.value:
    booking_filter = db.session.query(Booking).filter(
        (Booking.user_id == user.id)
        & (Booking.start_datetime > datetime.now())
        & (Booking.start_datetime < datetime.now() + timedelta(days=7))
    )
    booking_count = booking_filter.count()
    bookings = booking_filter.filter(
        (Booking.status == BookingStatus.confirmed.value)
    ).order_by(Booking.start_datetime.asc()).limit(6).all()

    top_news = db.session.query(News).order_by(
        News.published_at.desc()
    ).first()
    return render_template('user/dashboard.html',
                           user=user,
                           bookings=bookings,
                           greeting=greeting,
                           booking_count=booking_count,
                           reminder_count=reminder_count,
                           top_news=top_news
                           )

  today = datetime.combine(datetime.today(), datetime.min.time())
  start_of_week = today - timedelta(days=today.weekday())
  next_month = start_of_week.replace(
      month=start_of_week.month + 1) - timedelta(days=1)

  if user.role == Role.tutor.value:
    schedules = db.session.query(Schedule).filter(
        (Schedule.tutor_id == user.id)
        & ((Schedule.lesson_id != None) | (Schedule.workshop_id != None))
        & (Schedule.start_datetime >= start_of_week)
        & (Schedule.start_datetime <= next_month)
    ).order_by(Schedule.start_datetime.asc()).all()

    time_table = build_time_table_of_this_month(schedules)
    top_news = db.session.query(News).order_by(
        News.published_at.desc()
    ).first()
    return render_template('tutor/dashboard.html',
                           top_news=top_news,
                           user=user,
                           time_table=time_table,
                           greeting=greeting,
                           reminder_count=reminder_count)

  if user.role == Role.manager.value:

    schedules = db.session.query(Schedule).filter(
        ((Schedule.lesson_id != None) | (Schedule.workshop_id != None))
        & (Schedule.start_datetime >= start_of_week)
        & (Schedule.start_datetime <= next_month)
    ).order_by(Schedule.start_datetime.asc()).all()

    expiring_subscriptions = db.session.query(
        func.max(UserSubscription.end_datetime).label('end_datetime'),
        UserSubscription.user_id
    ).filter(
        (UserSubscription.end_datetime <= (datetime.now() + timedelta(days=7)))
    ).group_by(
        UserSubscription.user_id
    ).count()

    time_table = build_time_table_of_this_month(schedules)
    return render_template('manager/dashboard.html',
                           user=user,
                           time_table=time_table,
                           greeting=greeting,
                           reminder_count=reminder_count,
                           expiring_subscriptions=expiring_subscriptions
                           )


@user_view.route('/profile', defaults={'user_id': None})
@user_view.route('/profile/<int:user_id>')
@require_login()
def profile(user_id):
  if user_id is None:

    user_id = get_current_user().id

  member = User.query.get_or_404(user_id)

  return render_template('user/profile.html', member=member)


@user_view.route('/editprofile', methods=['GET', 'POST'])
def edit_profile():
  form = EditProfileForm()  # Instantiate the EditProfileForm
  user = get_current_user()

  is_tutor = user.role == 'tutor'

  form = EditProfileForm(is_tutor=is_tutor)

  # calculate user's age based on their date_of_birth and check if their experience is greater than their age
  if request.method == 'POST':

    # Parse and validate the date of birth for age check
    date_of_birth_str = request.form.get('date_of_birth')
    try:
      date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d')
      eighteen_years_ago = datetime.now() - timedelta(days=18 *
                                                      365.25)  # Consider leap years
      if date_of_birth > eighteen_years_ago:
        flash('You must be at least 18 years old.', 'danger')
        return render_template('user/edit_profile.html', form=form, is_tutor=is_tutor)
    except ValueError as e:
      flash('Invalid date of birth format.', 'danger')
      return render_template('user/edit_profile.html', form=form, is_tutor=is_tutor)

    if form.validate():
      if is_tutor:
        dob = form.date_of_birth.data
        today = date.today()
        age = today.year - dob.year - \
            ((today.month, today.day) < (dob.month, dob.day))
        if int(form.years_of_experience.data) > age:
          flash('Years of experience cannot be greater than your age.', 'danger')
          return render_template('user/edit_profile.html', form=form, is_tutor=is_tutor)

    # Handle form submission
    user.title = form.title.data
    user.first_name = form.first_name.data
    user.last_name = form.last_name.data
    user.position = form.position.data
    user.phone_number = form.phone_number.data
    user.email = form.email.data
    user.address = form.address.data
    user.date_of_birth = form.date_of_birth.data

    # Add on tutor's extra sections
    if user.role == 'tutor':
      user.teaching_subjects = form.teaching_subjects.data
      user.years_of_experience = form.years_of_experience.data
      user.qualification = form.qualification.data
      user.introduction = form.introduction.data

    # Commit changes to the database, commented out until login module available
    db.session.merge(user)
    db.session.commit()

    # Redirect to the profile page after successful edit
    flash('Profile updated successfully!', 'success')
    return redirect(url_for('user_view.profile'))

  # Pre-fill the form with current user's information
  form.title.data = user.title
  form.first_name.data = user.first_name
  form.last_name.data = user.last_name
  form.position.data = user.position
  form.phone_number.data = user.phone_number
  form.email.data = user.email
  form.address.data = user.address
  form.date_of_birth.data = user.date_of_birth

  # Pre-fill the form with tutor's information if the user is a tutor
  if user.role == 'tutor':
    form.teaching_subjects.data = user.teaching_subjects
    form.years_of_experience.data = user.years_of_experience
    form.qualification.data = user.qualification
    form.introduction.data = user.introduction

  return render_template('user/edit_profile.html', form=form, is_tutor=user.role == 'tutor')


@user_view.route('/logout')
def logout():
  session.clear()
  # Flash a success message to be displayed on the next rendered page
  flash('Successfully log out!', 'success')
  # Redirect the user to the login page after logging out
  return redirect(url_for('user_view.login'))


@user_view.route('/listtutors')
def list_tutors():
  # Query the database to get all users with the role of 'tutor'
  tutors = db.session.query(User).filter(User.role == 'tutor').all()
  # Render the HTML template 'list_tutors.html' and pass the list of tutors to it
  return render_template('user/list_tutors.html', tutors=tutors)


@user_view.route('/listworkshops')
def list_workshops():
  # Query the database to get all workshops
  workshops = db.session.query(Workshop).all()
  # Render the HTML template 'list_workshops.html' and pass the list of workshops to it
  return render_template('user/list_workshops.html', workshops=workshops)


@user_view.route('/search', methods=['GET'])
def search():
    #  Get the user-selected option and the entered search term
  category = request.args.get('category')
  query = request.args.get('query')
  # if input nothing
  if query == '':
    flash("Please input a name for search", 'danger')
    return redirect(url_for('homepage'))

  if category == 'tutor':
    # Using the ilike function for case-insensitive string matching
    tutors = db.session.query(User).filter(
        (User.role == 'tutor') &
        (func.lower(User.first_name).ilike(f'%{query.lower()}%') |
         func.lower(User.last_name).ilike(f'%{query.lower()}%'))
    ).all()
    if not tutors:
      flash("Can't find any tutor matches", 'danger')
      return redirect(url_for('homepage'))
    else:
      flash("Tutors found", 'success')
    return render_template('user/list_tutors.html', tutors=tutors)

  elif category == 'workshop':
    # Using the ilike function for case-insensitive string matching
    workshops = db.session.query(Workshop).filter(
        func.lower(Workshop.title).ilike(f'%{query.lower()}%')
    ).all()
    if not workshops:
      flash("Can't find any workshop matches", 'danger')
      return redirect(url_for('homepage'))
    else:
      flash("Workshops found", 'success')
    return render_template('user/list_workshops.html', workshops=workshops)


@user_view.route('/reminders', methods=['GET'], defaults={'page': 1})
@user_view.route('/reminders/<int:page>', methods=['GET'])
@require_login()
def list_reminders(page: int):
  user = get_current_user()
  reminders = db.session.query(Reminder).filter(
      Reminder.receiver_id == user.id
  ).order_by(
      Reminder.reminded_at.desc()
  ).paginate(page=page, per_page=15)
  return render_template('user/reminders.html', reminders=reminders)
