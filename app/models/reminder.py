from datetime import datetime
from app.utils.string_helper import format_date, format_time
from enum import Enum
from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date, Enum as DBEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.booking import Booking


class ReminderType(Enum):
  general = 'general'
  booking = 'booking'
  subscription = 'subscription'


class Reminder(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  subject: Mapped[String] = mapped_column(String(255))
  content: Mapped[Text] = mapped_column(Text)
  reminded_at: Mapped[DateTime] = mapped_column(DateTime)
  receiver_id: Mapped[Integer] = mapped_column(
      ForeignKey('user.id'), nullable=False)
  receiver = relationship('User', back_populates='reminders',
                          foreign_keys='Reminder.receiver_id')
  sender_id: Mapped[Integer] = mapped_column(
      ForeignKey('user.id'), nullable=True)
  sender = relationship('User', back_populates='sent_reminders',
                        foreign_keys='Reminder.sender_id')
  read_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

  action_url: Mapped[String] = mapped_column(String(255), nullable=True)
  action_text: Mapped[String] = mapped_column(String(255), nullable=True)

  user_subscription_id: Mapped[Integer] = mapped_column(
      ForeignKey('user_subscription.id'), nullable=True)

  user_subscription = relationship(
      'UserSubscription', back_populates='reminders')
  booking_id = mapped_column(ForeignKey('booking.id'), nullable=True)
  booking = relationship('Booking', back_populates='reminders')

  type = mapped_column(DBEnum(
      ReminderType.general.value,
      ReminderType.booking.value,
      ReminderType.subscription.value
  ), default=ReminderType.general.value, nullable=False)

  @ classmethod
  def create_booking_reminder(cls, booking: Booking, sender_id: int | None = None, action_text: str | None = None, action_url: str | None = None):
    '''
    Create a reminder for a booking
    '''
    reminder = Reminder(
        subject=f'Booking {booking.status}',
        content=f'Your booking for {booking.type} "{booking.schedule.schedule_name}" on {format_date(booking.start_datetime)} at {format_time(booking.start_datetime)} has been {booking.status}.',
        reminded_at=datetime.now(),
        receiver_id=booking.user_id,
        sender_id=sender_id,
        action_url=action_url,
        action_text=action_text,
        type=ReminderType.booking.value
    )
    return reminder

  @classmethod
  def create_subscription_expiring(cls,
                                   user_id: int,
                                   sender_id: int | None = None,
                                   url_to_renew: str | None = None,
                                   action_text: str | None = None,
                                   expiry_days: int | None = None,
                                   ):
    '''
    Create a reminder for an expiring subscription
    '''
    expiry_day_text = f'{expiry_days} days' if expiry_days else 'soon'
    reminder = Reminder(
        subject='Subscription Expiring',
        content=f'Your subscription is expiring {expiry_day_text}. Please renew to retain access to our services.',
        reminded_at=datetime.now(),
        receiver_id=user_id,
        sender_id=sender_id,
        action_url=url_to_renew,
        action_text=action_text,
        type=ReminderType.subscription.value
    )
    return reminder

  @classmethod
  def create_subscription_expired(cls,
                                  user_id: int,
                                  sender_id: int | None = None,
                                  url_to_renew: str | None = None,
                                  action_text: str | None = None
                                  ):
    '''
    Create a reminder for an expired subscription
    '''
    reminder = Reminder(
        subject='Subscription Expired',
        content='Your subscription has expired. Please renew to regain access to our services.',
        reminded_at=datetime.now(),
        receiver_id=user_id,
        sender_id=sender_id,
        action_url=url_to_renew,
        action_text=action_text,
        type=ReminderType.subscription.value
    )
    return reminder

  @classmethod
  def create_subscription_active(cls,
                                 subscription,
                                 sender_id: int | None = None,
                                 ):
    '''
    Create a reminder for an active subscription
    '''
    end_datetime = subscription.end_datetime.strftime('%d %b %Y')
    reminder = Reminder(
        subject='Subscription Active',
        content=f'Your subscription is active until {end_datetime}. Please renew to retain access to our services.',
        reminded_at=datetime.now(),
        receiver_id=subscription.user_id,
        sender_id=sender_id,
        type=ReminderType.subscription.value
    )
    return reminder

  @classmethod
  def create_welcome_message(cls, user_id: int):
    '''
    Create a welcome message for a new user
    '''
    reminder = Reminder(
        subject='Welcome to Kiwi Merino!',
        content='Thank you for joining Kiwi Merino. We hope you enjoy our services.',
        reminded_at=datetime.now(),
        receiver_id=user_id
    )
    return reminder

  @property
  def sender_name(self):
    '''
    Get the name of the sender of the reminder
    '''
    if self.sender_id is None:
      return 'System'
    else:
      return self.sender.full_name
