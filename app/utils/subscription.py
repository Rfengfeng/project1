from app.models.user import User
from app.models.user_subscription import UserSubscription
from app.database import db
from datetime import datetime, timedelta


def get_expired_subscriptions():
  '''
    Get all the subscriptions that have expired
  '''
  return db.session.query(UserSubscription).filter(UserSubscription.end_datetime < datetime.now())


def get_about_to_expire_subscriptions():
  '''
    Get all the subscriptions that are about to expire in the next 7 days
  '''
  seven_days_from_now = datetime.now() + timedelta(days=7)

  return db.session.query(UserSubscription).filter(
      (UserSubscription.end_datetime >= datetime.now()) &
      (UserSubscription.end_datetime <= seven_days_from_now)
  )
