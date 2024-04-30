from sqlalchemy import func
import re
from datetime import datetime, timedelta, date
from flask import (
    Blueprint, request, render_template, flash, session, redirect, url_for,
)

from app.models import User, Schedule, Workshop
from app.models.lesson import Lesson
from app.database import db
from app.utils.session import get_current_user, require_login, require_roles

lesson_view = Blueprint('lesson_view', __name__)


@lesson_view.route('/<int:id>', methods=['GET'])
@require_login()
def lesson(id: int):
  '''
  Get the details of a lesson by ID
  '''
  lesson = Lesson.query.get(id)
  return render_template('lesson/view.html', lesson=lesson, page_title=lesson.title)


@lesson_view.route('/', methods=['GET'])
def lessons():
  '''
  Get a list of lessons that have not started yet
  '''
  lessons = db.session.query(Lesson).filter(
      Lesson.schedules.any(Schedule.start_datetime > datetime.now())
  ).all()

  return render_template('lesson/list_lesson.html', lessons=lessons)
