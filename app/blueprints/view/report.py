
from datetime import datetime, timedelta
from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import case, column, func, outerjoin
from tomlkit import date
from app.database import db
from app.models import user
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment
from app.models.schedule import Schedule
from app.models.user import Role, User
from app.models.workshop import Workshop
from app.utils.reports import aggregate_revenue
from app.utils.session import get_current_user

report_view = Blueprint('report_view', __name__)


@report_view.before_request
def check_user():
  '''
  Only allow managers to access the reports
  '''
  current_user = get_current_user()
  if not current_user or current_user.role != Role.manager.value:
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('user_view.login'))


@report_view.route('/')
def home():
  '''
  Get the total revenue for the last year and the current financial year
  '''

  last_year = datetime.now() - timedelta(days=365)

  # Select the year_month from the paid_at column
  year_month = func.extract('YEAR_MONTH', Payment.paid_at).label('year_month')
  monthly = db.session.query(
      year_month,
      func.sum(Payment.amount_paid -
               func.coalesce(Payment.refunded_amount, 0)).label('total_revenue'),
      case(
          (Payment.user_subscription_id.isnot(None), 'subscription'),
          (Booking.schedule.has(Schedule.workshop_id.isnot(None)), 'workshop'),
          (Booking.schedule.has(Schedule.lesson_id.isnot(None)), 'lesson'),
          else_=None
      ).label('item_type'),  # Categorize the revenue by item type
  ).outerjoin(
      Booking, (Payment.booking_id == Booking.id)
  ).outerjoin(
      Schedule, (Booking.schedule_id == Schedule.id)
  ).filter(
      year_month > int(last_year.strftime('%Y%m'))
  ).group_by(
      'year_month',
      'item_type'
  ).order_by(
      'year_month'
  ).all()

  financial_years = db.session.query(
      case(
          ((func.extract('MONTH', Payment.paid_at) < 4),
           func.extract('YEAR', Payment.paid_at) - 1),
          else_=func.extract('YEAR', Payment.paid_at)
      ).label('fy'),
      func.sum(Payment.amount_paid -
               func.coalesce(Payment.refunded_amount, 0)).label('total_revenue'),
      case(
          (Payment.user_subscription_id.isnot(None), 'subscription'),
          (Booking.schedule.has(Schedule.workshop_id.isnot(None)), 'workshop'),
          (Booking.schedule.has(Schedule.lesson_id.isnot(None)), 'lesson'),
          else_=None
      ).label('item_type'),
  ).outerjoin(
      Booking, (Payment.booking_id == Booking.id)
  ).outerjoin(
      Schedule, (Booking.schedule_id == Schedule.id)
  ).group_by(
      'fy',
      'item_type'
  ).order_by(
      'fy'
  ).all()

  (monthly_grand_totals, monthly_data) = aggregate_revenue(
      monthly, label_formatter=lambda x: str(x)[0:4] + '-' + str(x)[4:])

  (fy_grand_totals, fy_data) = aggregate_revenue(financial_years)

  return render_template('manager/reports.html',
                         monthly_grand_totals=monthly_grand_totals,
                         monthly_data=monthly_data,
                         fy_grand_totals=fy_grand_totals,
                         fy_data=fy_data
                         )


@report_view.route('/workshops')
def workshops():
  '''
  Get the top 10 workshops by booking and attendance rate
  '''

  # Get the date range from the query string
  date_start = request.args.get('date_start', None)
  date_end = request.args.get('date_end', None)

  # Convert the date strings to datetime objects
  date_start = datetime.strptime(
      date_start, '%Y-%m-%d') if date_start else None
  date_end = datetime.strptime(date_end, '%Y-%m-%d') if date_end else None

  # If the date range is not provided, default to the last year
  if (date_start is None) or (date_end is None):
    date_start = datetime.today() - timedelta(days=365)
    date_end = datetime.today()

  booking_count = func.count(Booking.id).label('booking_count')
  attended_count = func.count(
      case(
          (Booking.attended, 1),
          else_=None
      )
  ).label('attended_count')
  # Get the attendance data for each workshop
  workshops_rows = db.session.query(
      Workshop.id,
      Workshop.title,
      booking_count,
      attended_count,
      case(
          (booking_count > 0, attended_count / booking_count),
          else_=0
      ).label('attendance_rate')
  ).join(
      Schedule, Workshop.id == Schedule.workshop_id
  ).join(
      Booking, Schedule.id == Booking.schedule_id
  ).filter(
      Booking.status == BookingStatus.confirmed.value,
      Booking.start_datetime >= date_start,
      Booking.start_datetime <= date_end
  ).group_by(
      Workshop.title, Workshop.id
  ).order_by(
      booking_count.desc()
  ).limit(
      10
  ).all()

  # Create a list of dictionaries to store the attendance data
  workshops = []
  for row in workshops_rows:
    workshops.append({
        'title': row.title,
        'workshop_id': row.id,
        'booking_count': row.booking_count,
        'attended_count': row.attended_count,
        'attendance_rate': row.attendance_rate
    })

  return render_template('manager/reports_workshops.html', workshops=workshops, date_start=date_start, date_end=date_end)


@report_view.route('/attendance')
def attendance():
  '''
  Generate a report of attendance for each user
  '''

  page = request.args.get('page', 1, type=int)
  # Get the date range from the query string
  date_start = request.args.get('date_start', None)
  date_end = request.args.get('date_end', None)

  # Convert the date strings to datetime objects
  date_start = datetime.strptime(
      date_start, '%Y-%m-%d') if date_start else None
  date_end = datetime.strptime(date_end, '%Y-%m-%d') if date_end else None

  # If the date range is not provided, default to the last year
  if (date_start is None) or (date_end is None):
    date_start = datetime.today() - timedelta(days=365)
    date_end = datetime.today()
  if date_end > datetime.today():
    date_end = datetime.today()

  booking_count = func.count(Booking.id).label('booking_count')
  user_name = func.concat(User.first_name, ' ',
                          User.last_name).label('user_name')
  # Get the attendance data for each user
  attendance_rows = db.session.query(
      user_name,
      User.id,
      booking_count,
      func.count(Schedule.lesson_id).label('lesson_booked'),
      func.count(
          case(
              ((Booking.attended == True) & (
                  Schedule.lesson_id.is_not(None)), 1),
              else_=None
          )).label('lesson_attended'),  # Count the number of lessons attended
      func.count(Schedule.workshop_id).label('workshop_booked'),
      func.count(
          case(
              ((Booking.attended == True) & (
                  Schedule.workshop_id.is_not(None)), 1),
              else_=None
          )).label('workshop_attended')  # Count the number of workshops attended
  ).join(
      Booking, User.id == Booking.user_id
  ).join(
      Schedule, Booking.schedule_id == Schedule.id
  ).filter(
      Booking.status == BookingStatus.confirmed.value,
      Booking.start_datetime < date_end,
      Booking.start_datetime > date_start
  ).group_by(
      user_name, User.id
  ).order_by(
      booking_count.desc()
  ).paginate(page=page, per_page=10)

  # Create a list of dictionaries to store the attendance data
  attendance_data = []

  for row in attendance_rows:
    attendance_data.append({
        'name': row.user_name,
        'user_id': row.id,
        'booking_count': row.booking_count,
        'lesson_booked': row.lesson_booked,
        'lesson_attended': row.lesson_attended,
        'workshop_booked': row.workshop_booked,
        'workshop_attended': row.workshop_attended,
        'lesson_attendance_rate': row.lesson_attended / row.lesson_booked if row.lesson_booked > 0 else 0,
        'workshop_attendance_rate': row.workshop_attended / row.workshop_booked if row.workshop_booked > 0 else 0,
        'overall_attendance_rate': (row.lesson_attended + row.workshop_attended) / (row.lesson_booked + row.workshop_booked) if (row.lesson_booked + row.workshop_booked) > 0 else 0,
    })

  return render_template('manager/reports_attendance.html',
                         attendance_data=attendance_data,
                         attendance_rows=attendance_rows,
                         date_start=date_start,
                         date_end=date_end
                         )
