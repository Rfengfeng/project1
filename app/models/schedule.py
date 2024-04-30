from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Schedule(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  start_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
  end_datetime: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
  cost: Mapped[Numeric] = mapped_column(Numeric(8, 2), default=0)

  lesson_id: Mapped[Integer] = mapped_column(ForeignKey(
      'lesson.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  lesson = relationship('Lesson', back_populates='schedules')

  workshop_id: Mapped[Integer] = mapped_column(ForeignKey(
      'workshop.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  workshop = relationship('Workshop', back_populates='schedules')

  tutor_id: Mapped[Integer] = mapped_column(ForeignKey(
      'user.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
  tutor = relationship('User', back_populates='schedules')

  bookings = relationship('Booking', back_populates='schedule')

  @property
  def schedule_name(self):
    '''
    Return the name of the schedule
    '''
    if self.lesson_id:
      return self.lesson.title
    if self.workshop_id:
      return self.workshop.title

    return 'Deleted Schedule'
