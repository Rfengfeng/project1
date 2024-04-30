from ast import arg
from flask import request
import email
import re
from decimal import Decimal
from datetime import datetime, timedelta, date, timezone
from flask import (
    Blueprint, request, render_template, flash, session, redirect, url_for,
)
from pkg_resources import require

from app.models import User, Schedule
from app.database import db
from app.models import subscription
from app.models import user_subscription
from app.models.booking import Booking
from app.models.lesson import Lesson
from app.models.reminder import Reminder, ReminderType
from app.models.user import Role, Position
from app.models.payment import Payment, PaymentStatus
from app.models.subscription import Subscription
from app.models.user_subscription import UserSubscription
from app.utils.session import get_current_user, require_login, require_roles
from app.utils.subscription import get_expired_subscriptions, get_about_to_expire_subscriptions


subscription_view = Blueprint('subscription_view', __name__)


def add_one_month(original_date):
  """Add a month to a date, handling month length variations."""
  # Attempt to get the same day next month
  try:
    next_month = original_date.replace(month=original_date.month + 1)
  except ValueError:
    if original_date.month == 12:
      # If December, roll over to January of next year
      next_month = original_date.replace(year=original_date.year + 1, month=1)
    else:
      # If next month is shorter, just go to the end of next month
      # Find the last day of the next month
      next_month = original_date.replace(
          month=original_date.month + 2, day=1) - timedelta(days=1)

  return next_month

# Route for displaying pricing for subscriptions based on user role


@subscription_view.route('/pricing/<int:user_id>', methods=['GET'])
def pricing(user_id):
  user = User.query.get(user_id)
  discount = 0

# Apply discount if user is a student or retired
  if user and user.position in ['student', 'retired']:
    discount = Decimal('0.30')

  subscriptions = Subscription.query.all()

# Calculate discounted prices for each subscription
  for subscription in subscriptions:
    original_price = Decimal(subscription.price)
    discounted_price = original_price - (original_price * discount)
    subscription.discounted_price = discounted_price.quantize(Decimal('0.1'))

  return render_template('user/pricing.html', subscriptions=subscriptions, discount=int(discount * 100), user=user)


@subscription_view.route('/checkout/<int:user_id>/<int:subscription_id>', methods=['GET', 'POST'])
def checkout(user_id, subscription_id):
  user = User.query.get(user_id)
  subscription = Subscription.query.get(subscription_id)

  if not user or not subscription:
    flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('subscription_view.pricing', user_id=user_id))

  if request.method == 'POST':

    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    address = request.form.get('address')
    address2 = request.form.get('address2')
    country = request.form.get('country')
    state = request.form.get('state')
    suburb = request.form.get('suburb')
    postcode = request.form.get('postcode')
    payment_type = request.form.get('paymentMethod')
    cc_name = request.form.get('cc-name')
    cc_number = request.form.get(
        'cc-number', '').replace(' ', '').replace('-', '')
    cc_expiration = request.form.get('cc-expiration')

    card_pattern = re.compile(r'^\d{13,19}$')
    if not card_pattern.match(cc_number):
      flash('Please check the credit card number.', 'danger')
      return render_template('user/checkout.html', user=user, user_id=user_id, subscription=subscription, subscription_id=subscription_id)

    start_datetime = datetime.now()

    latest_subscription = UserSubscription.query.filter(
        (UserSubscription.user_id == user.id) & (
            UserSubscription.end_datetime > datetime.now())
    ).order_by(UserSubscription.end_datetime.desc()).first()

    if latest_subscription:
      start_datetime = latest_subscription.end_datetime

    end_datetime = start_datetime + timedelta(days=subscription.duration)

    user_subscription = UserSubscription(
        user_id=user.id,
        subscription_id=subscription.id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        cost=subscription.price,
        amount_paid=subscription.price
    )
    user.membership_expiry = end_datetime
    db.session.add(user_subscription)
    db.session.flush()

    payment = Payment(
        user_id=user_id,
        user_subscription_id=user_subscription.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        address=address,
        address2=address2,
        country=country,
        state=state,
        suburb=suburb,
        postcode=postcode,
        payment_type=payment_type,
        name_on_card=cc_name,
        card_number=cc_number[-4:],
        expiration_date=cc_expiration,
        paid_at=datetime.now(timezone.utc),
        status=PaymentStatus.completed.value,
        amount_paid=subscription.price,
    )
    db.session.add(payment)
    reminder = Reminder.create_subscription_active(
        subscription=user_subscription,
    )
    db.session.add(reminder)

# Update user status and commit all changes to the database
    user.active = True
    db.session.commit()

    session['user'] = user.to_dict()
    flash('Payment successful! Welcome.', 'success')
    return redirect(url_for('user_view.dashboard'))

  return render_template('user/checkout.html', user=user, user_id=user_id, subscription=subscription, subscription_id=subscription_id)


@ subscription_view.route('/subscription_details')
def subscription_details():
  user_id = request.args.get('user_id')
  user = User.query.get(user_id)
  if not user:
    flash('User not found', 'danger')
    return redirect(url_for('user_view.login'))

  user_subscription = UserSubscription.query.filter_by(
      user_id=user.id).order_by(UserSubscription.end_datetime.desc()).first()

  subscription = user_subscription.subscription

  return render_template('user/subscription_details.html', user=user, user_id=user.id, subscription=subscription, user_subscription=user_subscription)


@subscription_view.route('/renew_subscription/<int:user_id>', methods=['GET', 'POST'])
def renew_subscription(user_id):
  user = User.query.get(user_id)
  if not user:
    flash('User not found.', 'danger')
    return redirect(url_for('main.index'))

  discount = Decimal('0.30') if user.position in [
      'student', 'retired'] else Decimal('0.00')

  subscriptions = Subscription.query.all()
  for subscription in subscriptions:
    original_price = Decimal(subscription.price)
    discounted_price = original_price - (original_price * discount)
    subscription.discounted_price = discounted_price.quantize(Decimal('0.1'))

  return render_template('user/renew_subscription.html', subscriptions=subscriptions, user=user, discount=int(discount * 100))


@subscription_view.route('/renew_checkout/<int:user_id>/<int:subscription_id>', methods=['GET', 'POST'])
def renew_checkout(user_id, subscription_id):
  user = User.query.get(user_id)
  subscription = Subscription.query.get(subscription_id)

  if not user or not subscription:
    flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('subscription_view.renew_subscription', user_id=user_id))

  if request.method == 'POST':
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    email = request.form.get('email')
    address = request.form.get('address')
    address2 = request.form.get('address2')
    country = request.form.get('country')
    state = request.form.get('state')
    suburb = request.form.get('suburb')
    postcode = request.form.get('postcode')
    payment_type = request.form.get('paymentMethod')
    cc_name = request.form.get('cc-name')
    cc_number = request.form.get(
        'cc-number', '').replace(' ', '').replace('-', '')
    cc_expiration = request.form.get('cc-expiration')

    start_datetime = datetime.now()

    latest_subscription = UserSubscription.query.filter(
        (UserSubscription.user_id == user.id) & (
            UserSubscription.end_datetime > datetime.now())
    ).order_by(UserSubscription.end_datetime.desc()).first()

    if latest_subscription:
      start_datetime = latest_subscription.end_datetime

    end_datetime = start_datetime + timedelta(days=subscription.duration)

    # Create new subscription in db
    user_subscription = UserSubscription(
        user_id=user.id,
        subscription_id=subscription.id,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        cost=subscription.price,
        amount_paid=subscription.price
    )
    db.session.add(user_subscription)
    db.session.flush()

    # Create new payment in db
    new_payment = Payment(
        user_id=user_id,
        user_subscription_id=user_subscription.id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        address=address,
        address2=address2,
        country=country,
        state=state,
        suburb=suburb,
        postcode=postcode,
        payment_type=payment_type,
        name_on_card=cc_name,
        card_number=cc_number[-4:],
        expiration_date=cc_expiration,
        paid_at=datetime.now(timezone.utc),
        status=PaymentStatus.completed.value,
    )
    db.session.add(new_payment)
    db.session.flush()

    user.membership_expiry = end_datetime
    db.session.merge(user)

    db.session.commit()

    session['user'] = user.to_dict()
    flash('Your subscription has been successfully renewed.', 'success')
    return redirect(url_for('subscription_view.subscription_details', user_id=user.id))

  return render_template('user/renew_checkout.html', user=user, user_id=user_id, subscription=subscription, subscription_id=subscription_id)


@subscription_view.route('/payment_history/<int:user_id>', methods=['GET'])
def payment_history(user_id):
  user = User.query.get(user_id)
  if not user:
    flash('User not found', 'danger')
    return redirect(url_for('user_view.login'))

  # Join Payment, UserSubscription, and Subscription tables
  # Now also selecting amount_paid from UserSubscription
  payments = db.session.query(
      Payment,
      Subscription.title,
      UserSubscription.amount_paid,
      UserSubscription.start_datetime,
      UserSubscription.end_datetime
  ).join(
      UserSubscription, UserSubscription.id == Payment.user_subscription_id
  ).join(Subscription, Subscription.id == UserSubscription.subscription_id
         ).filter(
      Payment.user_id == user.id
  ).order_by(
      Payment.paid_at.desc()
  ).all()

  return render_template('user/payment_history.html', payments=payments, user=user, now=datetime.now())


@subscription_view.route('/list_expire', methods=['GET', 'POST'])
@require_roles([Role.manager])
def expired_subscriptions_get():
  # Page number for expired subscriptions
  expired_page = request.args.get('expired_page', 1, type=int)
  # Page number for subscriptions about to expire
  expiring = request.args.get('expiring_page', 1, type=int)
  per_page = 10  # Number of items per page

  search_query = request.form.get(
      'query') or request.args.get('query')  # Search query
  search_term = f'%{search_query}%' if search_query else None

  # Get base queries
  expired_subscriptions_query = get_expired_subscriptions()
  about_to_expire_subscriptions_query = get_about_to_expire_subscriptions()

  if search_term:
    # Retrieve members matching the search term
    members = db.session.query(User).filter(
        (User.role == Role.member.value) &
        (
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term)) |
            ((User.first_name + " " + User.last_name).ilike(search_term)) |
            (User.email.ilike(search_term))
        )
    ).all()

    member_ids = [member.id for member in members]  # Get member IDs

    # Filter subscriptions based on member IDs
    expired_subscriptions_query = expired_subscriptions_query.filter(
        UserSubscription.user_id.in_(member_ids))
    about_to_expire_subscriptions_query = about_to_expire_subscriptions_query.filter(
        UserSubscription.user_id.in_(member_ids))

  # Paginate filtered queries
  expired_subscriptions = expired_subscriptions_query.paginate(
      page=expired_page, per_page=per_page)
  about_to_expire_subscriptions = about_to_expire_subscriptions_query.paginate(
      page=expiring, per_page=per_page)

  reminding_user_ids = [sub.user_id for sub in expired_subscriptions.items] + \
      [sub.user_id for sub in about_to_expire_subscriptions.items]
  # Get reminders for subscriptions
  sent_reminders = db.session.query(Reminder).filter(
      Reminder.receiver_id.in_(reminding_user_ids)
      & (Reminder.type == ReminderType.subscription.value)
  ).order_by(
      Reminder.reminded_at.desc()
  ).all()
  # Create a dictionary of reminders for each user
  sent_reminder_dict = {}
  for reminder in sent_reminders:
    if reminder.receiver_id not in sent_reminder_dict:
      sent_reminder_dict[reminder.receiver_id] = reminder

  return render_template(
      'manager/expired_subscriptions.html',
      expired_subscriptions=expired_subscriptions,
      about_to_expire_subscriptions=about_to_expire_subscriptions,
      query=search_query,
      sent_reminders=sent_reminder_dict
  )
