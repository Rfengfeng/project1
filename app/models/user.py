from enum import Enum
from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date, Enum as DBEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import user_subscription
# from app.models.image import Image


class Role(Enum):
  manager = 'manager'
  tutor = 'tutor'
  member = 'member'


class Position(Enum):
  student = 'student'
  farmer = 'farmer'
  retired = 'retired'
  others = 'others'


class User(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  role: Mapped[String] = mapped_column(DBEnum(
      Role.manager.value, Role.tutor.value, Role.member.value), default=Role.member.value)
  first_name: Mapped[String] = mapped_column(String(32))
  last_name: Mapped[String] = mapped_column(String(32))
  title: Mapped[String] = mapped_column(String(32), nullable=True)
  position: Mapped[String] = mapped_column(String(32), nullable=True)
  phone_number: Mapped[String] = mapped_column(String(32), nullable=True)
  email: Mapped[String] = mapped_column(String(255), unique=True)
  address: Mapped[String] = mapped_column(String(255), nullable=True)
  date_of_birth: Mapped[Date] = mapped_column(Date, nullable=True)
  profile_image_id: Mapped[Integer] = mapped_column(
      ForeignKey('image.id'), nullable=True)
  profile_image = relationship('Image', back_populates='users')
  password: Mapped[String] = mapped_column(String(64))
  salt: Mapped[String] = mapped_column(String(32))
  lessons = relationship('Lesson', back_populates='tutor')
  active: Mapped[Boolean] = mapped_column(Boolean, default=True)
  reminders = relationship(
      'Reminder', back_populates='receiver', foreign_keys='Reminder.receiver_id')
  sent_reminders = relationship(
      'Reminder', back_populates='sender', foreign_keys='Reminder.sender_id')
  # Extra info for tutors
  teaching_subjects: Mapped[String] = mapped_column(String(255), nullable=True)
  years_of_experience: Mapped[String] = mapped_column(
      String(255), nullable=True)
  qualification: Mapped[String] = mapped_column(String(255), nullable=True)
  introduction: Mapped[Text] = mapped_column(Text, nullable=True)
  schedules = relationship(
      'Schedule', back_populates='tutor')
  bookings = relationship('Booking', back_populates='user')
  payments = relationship('Payment', back_populates='user')
  membership_expiry: Mapped[Date] = mapped_column(Date, nullable=True)
  news = relationship('News', back_populates='user')
  user_subscriptions = relationship('UserSubscription', back_populates='user')

  @classmethod
  def visible_columns(cls):
    '''
    Override the visible columns
    '''
    cols = cls.__table__.columns.keys()
    results = filter(lambda c: c not in ['password', 'salt'], cols)
    results = list(results) + ['full_name', 'profile_image_url']
    return results

  @property
  def full_name(self):
    '''
    Return the full name of the user
    '''
    return f"{self.first_name or ''} {self.last_name or ''}".strip()

  @property
  def profile_image_url(self):
    '''
    Return the profile image URL
    '''
    return self.profile_image.path if self.profile_image else 'img/default-profile.jpg'
