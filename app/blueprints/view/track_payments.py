import re
from decimal import Decimal
from flask import Blueprint, flash, redirect, url_for, render_template, request
from datetime import datetime, timedelta, date, timezone
from sqlalchemy import func, or_, case

from app.models.user import Role
from app.utils.session import get_current_user, require_login, require_roles
from app.models import User
from app.models import Payment
from app.models.payment import Payment
from app.models.booking import Booking, BookingStatus
from app.models.schedule import Schedule
from app.models.lesson import Lesson
from app.utils.session import get_current_user, require_login, require_roles, set_current_user
from app.models.subscription import Subscription
from app.models.user_subscription import UserSubscription
from app.models.user import Role, Position
from app.database import db


track_payments_view = Blueprint('track_payments_view', __name__)

# check whether user is a manager role


@track_payments_view.before_request
def check_user():
  current_user = get_current_user()
  if not current_user or current_user.role != Role.manager.value:
    flash('You are not authorized to view this page', 'danger')
    return redirect(url_for('user_view.login'))


@track_payments_view.route('/payment-tracking', methods=['GET'])
def track_payments():
  page = request.args.get('page', 1, type=int)
  per_page = 10
  search_query = request.args.get('search', '', type=str)

# Construct the base query to retrieve payment and related user information from the database
  base_query = db.session.query(
      Payment.paid_at,
      User.first_name,
      User.last_name,
      User.email,
      User.id.label('user_id'),
      Payment.status,
      Payment.id,
      Payment.amount_paid,
      Payment.refunded_amount,
      Payment.refunded_at,
      case(
          (UserSubscription.id.isnot(None), 'Subscription'),
          (Booking.schedule.has(Schedule.lesson_id.isnot(None)), 'Lesson'),
          (Booking.schedule.has(Schedule.workshop_id.isnot(None)), 'Workshop'),
          else_='Unknown'
      ).label('payment_type'),
      Subscription.title.label('item_purchased'),
      Lesson.title.label('lesson_purchased')
  ).outerjoin(UserSubscription, UserSubscription.id == Payment.user_subscription_id)\
      .outerjoin(Subscription, Subscription.id == UserSubscription.subscription_id)\
      .outerjoin(User, Payment.user_id == User.id)\
      .outerjoin(Booking, Booking.id == Payment.booking_id)\
      .outerjoin(Schedule, Schedule.id == Booking.schedule_id)\
      .outerjoin(Lesson, Lesson.id == Schedule.lesson_id)

  if search_query:
    search = f"%{search_query}%"
    base_query = base_query.filter(
        or_(
            User.first_name.ilike(search),
            User.last_name.ilike(search),
            Subscription.title.ilike(search),
            Lesson.title.ilike(search)
        )
    )

  payments_info = base_query.order_by(Payment.paid_at.desc()).paginate(
      page=page, per_page=per_page, error_out=False)

  return render_template('manager/track_payments.html', payments=payments_info, search_query=search_query)

# Route to handle requests for details of a specific payment by its ID


@track_payments_view.route('/payment-details/<int:payment_id>', methods=['GET'])
def payment_details(payment_id):
  payment = db.session.query(Payment).get(payment_id)

  if not payment:
    flash('Payment details not found.', 'warning')
    return redirect(url_for('track_payments_view.track_payments'))

  return render_template('manager/payment_details.html', payment=payment)
