
from datetime import datetime
import re
from flask import Blueprint, request, url_for

from app.models.reminder import Reminder
from app.models.user_subscription import UserSubscription
from app.utils.session import get_current_user, require_login, require_roles
from app.database import db
from app.models.user import Role


reminder_api = Blueprint('reminder_api', __name__)


@reminder_api.route('unread/count', methods=['GET'])
@require_login()
def get_unread_reminders():
  '''
  Get the count of unread reminders for the current user
  '''
  user = get_current_user()
  reminders = db.session.query(Reminder).filter(
      (Reminder.receiver_id == user.id)
      & (Reminder.read_at == None)
  ).count()

  return {'success': True, 'reminders': reminders}


@reminder_api.route('<int:id>', methods=['GET'])
@require_login()
def get_reminder(id: int):
  '''
  Get a reminder by ID
  '''
  user = get_current_user()
  reminder = db.session.query(Reminder).get(id)

  if not reminder:
    return {'success': False, 'error': 'Reminder not found'}

  if reminder.receiver_id != user.id and user.role != Role.manager.value:
    return {'success': False, 'error': 'Unauthorized'}

  return {'success': True, 'reminder': reminder.to_dict()}


@reminder_api.route('<int:id>', methods=['DELETE'])
@require_login()
def delete_reminder(id: int):
  '''
  Delete a reminder by ID
  '''
  user = get_current_user()
  reminder = db.session.query(Reminder).get(id)

  if not reminder:
    return {'success': False, 'error': 'Reminder not found'}

  if reminder.user_id != user.id and user.role != Role.manager.value:
    return {'success': False, 'error': 'Unauthorized'}

  db.session.delete(reminder)
  db.session.commit()
  return {'success': True}


@reminder_api.route('<int:id>/read', methods=['POST'])
@require_login()
def mark_as_read(id: int):
  '''
  Mark a reminder as read by ID
  '''
  user = get_current_user()
  reminder = db.session.query(Reminder).get(id)

  # Return an error if the reminder is not found
  if not reminder:
    return {'success': False, 'error': 'Reminder not found'}

  # Return an error if the user is not the receiver of the reminder
  if reminder.receiver_id != user.id and user.role != Role.manager.value:
    return {'success': False, 'error': 'Unauthorized'}

  reminder.read_at = datetime.now()
  db.session.merge(reminder)
  db.session.commit()

  return {'success': True, 'reminder': reminder.to_dict(), 'read_at': reminder.read_at.strftime('%d %b %Y %I:%M %p')}


@reminder_api.route('/subscription/<int:id>', methods=['POST'])
@require_roles([Role.manager])
def send_subscription_reminder(id):
  '''
  Send a reminder to renew a subscription by subscription ID
  '''
  user = get_current_user()
  subscription = db.session.query(UserSubscription).get(id)
  reminder = None

  if subscription.end_datetime < datetime.now():
    # Create a reminder for the subscription expired
    reminder = Reminder.create_subscription_expired(
        action_text='Renew Subscription',
        sender_id=user.id,
        user_id=subscription.user_id,
        url_to_renew=url_for(
            'subscription_view.renew_subscription', user_id=subscription.user_id)
    )
  else:
    # Create a reminder for the subscription expiring
    reminder = Reminder.create_subscription_expiring(
        action_text='Renew Subscription',
        sender_id=user.id,
        user_id=subscription.user_id,
        url_to_renew=url_for(
            'subscription_view.renew_subscription', user_id=subscription.user_id),
        expiry_days=(subscription.end_datetime - datetime.now()).days
    )

  db.session.add(reminder)
  db.session.commit()
  return {'success': True, 'message': 'Reminder sent successfully'}
