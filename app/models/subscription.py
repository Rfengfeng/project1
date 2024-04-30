from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Subscription(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  title: Mapped[String] = mapped_column(String(255), nullable=True)
  price: Mapped[Numeric] = mapped_column(
      Numeric(8, 2), nullable=False, default=0.00)
  duration: Mapped[Integer] = mapped_column(Integer, nullable=False, default=0)
  description: Mapped[String] = mapped_column(String(255), nullable=True)
  user_subscriptions = relationship(
      'UserSubscription', back_populates='subscription')
