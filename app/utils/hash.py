import hashlib
import json
import re

from flask_hashing import Hashing

hashing = Hashing()


def generate_password_hash(password, salt):
  """
  Generate password hash
  :param password:
  :param salt:
  :return:
  """
  return hashing.hash_value(password, salt=salt)


def is_strong_password(password):
  """
  password must be at least 8 characters long and have a mix of character types
  :param password:
  :return:
  """
  # check if password is at least 8 characters long
  if len(password) < 8:
    return False

  # check if password contains letter and digit
  if not re.search(r'[A-Za-z]', password) or \
          not re.search(r'\d', password):
    return False

  return True


def str_to_json(string):
  """
  parse string to json
  :param string:
  :return:
  """
  try:
    return json.loads(string)
  except json.JSONDecodeError:
    return []
