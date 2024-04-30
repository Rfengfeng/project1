from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import reminder


class UserSubscription(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  user_id: Mapped[Integer] = mapped_column(
      ForeignKey('user.id'), nullable=False)
  user = relationship('User', back_populates='user_subscriptions')
  subscription_id: Mapped[Integer] = mapped_column(
      ForeignKey('subscription.id'), nullable=False)
  subscription = relationship(
      'Subscription', back_populates='user_subscriptions')
  start_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
  end_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
  cost: Mapped[Numeric] = mapped_column(Numeric(8, 2), nullable=True)
  amount_paid: Mapped[Numeric] = mapped_column(Numeric(8, 2), nullable=True)

  payments = relationship('Payment', back_populates='user_subscription')
  reminders = relationship('Reminder', back_populates='user_subscription')
