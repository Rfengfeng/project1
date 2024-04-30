from math import exp
from re import sub
from xml.etree.ElementTree import iselement

from flask import url_for
from app.models.reminder import Reminder, ReminderType
from app.models.user import User
from datetime import datetime, timedelta

from app.database import db
from app.models.user_subscription import UserSubscription

expiry_threshold = timedelta(days=7)


def create_subscription_reminder(user: User) -> Reminder | None:
  # Check if the user has an active subscription
  action_url = url_for('subscription_view.pricing', user_id=user.id)
  action_text = 'Subscribe Now'

  if user.membership_expiry and user.membership_expiry > (datetime.now() + expiry_threshold):
    return None

  # Check if the user's subscription is expired
  is_expired = (user.membership_expiry is None) or (
      user.membership_expiry < datetime.now())

  # Get the last reminder for the user
  last_reminded = db.session.query(Reminder).filter(
      (Reminder.receiver_id == user.id)
      & (Reminder.type == ReminderType.subscription.value)
      & (Reminder.reminded_at > datetime.now() - expiry_threshold)
  )

  if user.membership_expiry and is_expired:
    # Filter out the expiring reminders
    last_reminded = last_reminded.filter(
        (Reminder.reminded_at < user.membership_expiry - expiry_threshold)
        | (Reminder.reminded_at > user.membership_expiry)
    )

  if last_reminded.first():
    return None

  # Get the last subscription for the user
  last_subscription = db.session.query(UserSubscription).filter(
      UserSubscription.user_id == user.id,
  ).order_by(UserSubscription.end_datetime.desc()).first()

  # Create a reminder for the user
  reminder = Reminder.create_subscription_expired(
      user_id=user.id,
      url_to_renew=action_url,
      action_text=action_text,
  ) if is_expired else Reminder.create_subscription_expiring(
      user_id=user.id,
      url_to_renew=action_url,
      action_text=action_text,
      expiry_days=(user.membership_expiry - datetime.now()).days
  )

  # If the user has never subscribed, remind them to subscribe
  if user.membership_expiry is None:
    reminder.subject = 'Subscribe to access our services'
    reminder.content = 'You are not subscribed to our services. Subscribe now to access our services.'

  # Set the user subscription ID for the reminder
  if last_subscription:
    reminder.user_subscription_id = last_subscription.id

  db.session.add(reminder)
  db.session.flush()
  return reminder
