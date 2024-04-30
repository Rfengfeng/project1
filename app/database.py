from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = None


def dict_value(value):
  if isinstance(value, db.Model):
    return value.to_dict()
  elif isinstance(value, datetime):
    return value.isoformat()
  elif isinstance(value, date):
    return value.isoformat()
  elif isinstance(value, list):
    return [dict_value(v) for v in value]
  else:
    return value


class Base(DeclarativeBase):
  @classmethod
  def visible_columns(cls):
    return cls.__table__.columns.keys()

  def to_dict(self):
    cols = self.visible_columns()
    result = {}
    for col in cols:
      value = getattr(self, col)
      result[col] = dict_value(value)
    return result


db = SQLAlchemy(model_class=Base)
