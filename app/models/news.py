from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship


class News(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  title: Mapped[String] = mapped_column(String(255), nullable=True)
  content: Mapped[Text] = mapped_column(Text, nullable=True)
  published_at: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
  author: Mapped[String] = mapped_column(String(64), nullable=True)
  user_id: Mapped[Integer] = mapped_column(
      Integer, ForeignKey('user.id'), nullable=False)
  user = relationship('User', back_populates='news')
