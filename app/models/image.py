from isort import file
from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
import os


class Image(db.Model):
  __tablename__ = 'image'
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  title: Mapped[String] = mapped_column(String(64), nullable=True)
  path: Mapped[String] = mapped_column(String(255), nullable=True)
  created_at: Mapped[DateTime] = mapped_column(
      DateTime, nullable=False, server_default='now()')
  size: Mapped[Integer] = mapped_column(Integer, nullable=True)
  users = relationship('User', back_populates='profile_image')

  def delete(self, db_session):
    '''
    Delete the image file and the database record
    '''
    image_path_arr = self.path.split('/')
    file_path = os.path.join('app', 'static', 'uploads', image_path_arr[-1])

    # Delete the file
    if file_path:
      try:
        os.remove(file_path)
      except Exception as e:
        print(e)
        pass
    db_session.delete(self)
