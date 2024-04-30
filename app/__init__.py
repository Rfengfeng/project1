from datetime import datetime, timedelta
from flask import Flask, flash, render_template, request
from regex import P
from app import blueprints
from app.database import db
from app import connect
from flask_migrate import Migrate
from urllib.parse import quote
import os
import time

from app.models.schedule import Schedule
from app.utils.timetable import build_time_table_of_this_month

os.environ["TZ"] = "Pacific/Auckland"

try:
  time.tzset()
except:
  # Windows does not support time.tzset()
  pass

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+mysqlconnector://{quote(connect.dbuser)}:{quote(connect.dbpass)}@{connect.dbhost}/{connect.dbname}"

app.jinja_env.globals['site_name'] = 'Kiwi Merino - A Merino Breeders Society'
app.jinja_env.globals['datetime_format'] = '%d %b %Y %I:%M %p'
app.jinja_env.globals['time_format'] = '%I:%M %p'
app.jinja_env.globals['date_format'] = '%d %b %Y'

db.init_app(app)

migrate = Migrate(app, db)

# Register all API below
app.register_blueprint(blueprints.user_api, url_prefix='/api/user')
app.register_blueprint(blueprints.booking_api, url_prefix='/api/booking')
app.register_blueprint(blueprints.reminder_api, url_prefix='/api/reminder')

# Register all view below
app.register_blueprint(blueprints.user_view, url_prefix='/user')
app.register_blueprint(blueprints.lesson_view, url_prefix='/lesson')
app.register_blueprint(blueprints.booking_view, url_prefix='/booking')
app.register_blueprint(blueprints.manager_view, url_prefix='/manager')
app.register_blueprint(blueprints.tutor_view, url_prefix='/tutor')
app.register_blueprint(blueprints.subscription_view,
                       url_prefix='/subscription')
app.register_blueprint(blueprints.member_view, url_prefix='/member')
app.register_blueprint(blueprints.payment_view, url_prefix='/payment')
app.register_blueprint(blueprints.schedule_view, url_prefix='/schedule')
app.register_blueprint(blueprints.location_view, url_prefix='/location')
app.register_blueprint(blueprints.news_view, url_prefix='/news')
app.register_blueprint(blueprints.track_payments_view,
                       url_prefix='/track-payments')
app.register_blueprint(blueprints.report_view, url_prefix='/report')


@app.route('/')
def homepage():
  # Index page
  today = datetime.today()
  start_of_week = today - timedelta(days=today.weekday())
  next_month = start_of_week.replace(
      month=start_of_week.month + 1) - timedelta(days=1)

  schedules = db.session.query(Schedule).filter(
      ((Schedule.lesson_id != None) | (Schedule.workshop_id != None))
      & (Schedule.start_datetime >= start_of_week)
      & (Schedule.start_datetime <= next_month)
  ).order_by(
      Schedule.start_datetime.asc()
  ).all()
  table_entries = build_time_table_of_this_month(schedules)
  return render_template('index.html', table_entries=table_entries)


# # Create all tables
# with app.app_context():
#   db.create_all()

# Check if there is a flash message in the query string
# Set the flash message if it exists


def check_flash_message():
  flash_message = request.args.get('_fm')
  flash_category = request.args.get('_fc', 'primary')
  if flash_message:
    flash(flash_message, category=flash_category)


app.before_request_funcs.setdefault(None, []).append(check_flash_message)
