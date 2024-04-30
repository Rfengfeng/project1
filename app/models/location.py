
from app.database import db
from sqlalchemy import Integer, String, DateTime, Numeric, Boolean, ForeignKey, Text, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models import workshop


class Location(db.Model):
  id: Mapped[Integer] = mapped_column(
      Integer, primary_key=True, autoincrement=True)
  title: Mapped[String] = mapped_column(String(64), nullable=True)
  address1: Mapped[String] = mapped_column(String(64), nullable=True)
  address2: Mapped[String] = mapped_column(String(64), nullable=True)
  suburb: Mapped[String] = mapped_column(String(32), nullable=True)
  city: Mapped[String] = mapped_column(String(32), nullable=True)
  region: Mapped[String] = mapped_column(String(32), nullable=True)
  state: Mapped[String] = mapped_column(String(32), nullable=True)
  postcode: Mapped[String] = mapped_column(String(32), nullable=True)
  workshops = relationship('Workshop', back_populates='location')
  facilities: Mapped[Text] = mapped_column(Text, nullable=True)

  def __str__(self) -> str:
    '''
    Return the full address with the title
    '''
    arr = [
        self.title,
        self.address1,
        self.address2,
        self.suburb,
        self.city,
        self.region,
        self.state,
    ]

    # filter emtpy or None values
    str = ', '.join(list(filter(lambda x: not not x, arr)))
    return str + f" {self.postcode}"

  @property
  def full_address(self) -> str:
    '''
    Return the full address
    '''
    arr = [
        self.address1,
        self.address2,
        self.suburb,
        self.city,
        self.region,
        self.state,
    ]

    # filter emtpy or None values
    str = ', '.join(list(filter(lambda x: not not x, arr)))
    return str + f" {self.postcode}"
