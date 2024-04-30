from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Workshop(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  title: Mapped[String] = mapped_column(String(32), nullable=True)

  location_id: Mapped[Integer] = mapped_column(ForeignKey(
      'location.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  location = relationship('Location', back_populates='workshops')

  price: Mapped[Numeric] = mapped_column(
      Numeric(8, 2), nullable=False, default=0.00)

  schedules = relationship('Schedule', back_populates='workshop')
  description: Mapped[Text] = mapped_column(Text, nullable=True)
