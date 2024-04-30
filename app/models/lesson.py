from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date, desc
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Lesson(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  title: Mapped[String] = mapped_column(String(64), nullable=True)
  tutor_id: Mapped[Integer] = mapped_column(
      Integer, ForeignKey('user.id'), nullable=True)
  cost: Mapped[Numeric] = mapped_column(Numeric(8, 2), default=0)
  lesson_number: Mapped[String] = mapped_column(String(32))
  tutor = relationship('User', back_populates='lessons')
  schedules = relationship('Schedule', back_populates='lesson')
  description: Mapped[Text] = mapped_column(Text, nullable=True)
