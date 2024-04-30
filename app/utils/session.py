
from datetime import datetime
from functools import wraps
import re
from app.models.user import Role, User
from flask import request, session, redirect, url_for, flash
from app.database import db
from urllib.parse import quote


def check_roles(roles: list[Role]) -> bool:
  '''
  Check if a user has a certain role
  '''
  user = session.get('user')
  if user is None:
    return False
  return user.role in [role.value for role in roles]


def require_roles(roles: list[Role]):
  '''
  A decorator that requires a user to have a certain role to access a route
  '''
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
      if 'user' not in session:
        return redirect(url_for('user_view.login', next=(request.url or ''))) if not is_ajax else ('Unauthorized', 401)
      if roles and session['user']['role'] not in [role.value for role in roles]:
        return redirect(url_for('user_view.login', next=(request.url or ''))) if not is_ajax else ('Unauthorized', 401)
      return f(*args, **kwargs)
    return decorated_function
  return decorator


def require_login():
  '''
  A decorator that requires a user to be logged in to access a route
  '''
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
      if 'user' not in session:
        return redirect(url_for('user_view.login', next=(request.url or ''))) if not is_ajax else ('Unauthorized', 401)
      return f(*args, **kwargs)
    return decorated_function
  return decorator


def get_current_user() -> User | None:
  '''
  Get the current user from the session
  :return: The current user or None
  '''
  if not session.get('user'):
    return None
  return db.session.query(User).get(session['user']['id'])


def set_current_user(user: User):
  '''
  Set the current user in the session
  :param user: The user to set
  '''
  session['user'] = user.to_dict() if user else None
  return user


def require_membership():
  '''
  A decorator that requires a user to have an active membership to access a route
  '''
  def decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
      user = get_current_user()
      if not user:
        return redirect(url_for('user_view.login', next=(request.url or '')))
      if user.membership_expiry is None or user.membership_expiry < datetime.today():
        flash('You need an active membership to access this page', 'danger')
        return redirect(url_for('subscription_view.pricing', user_id=user.id))
      return f(*args, **kwargs)
    return decorated_function
  return decorator
