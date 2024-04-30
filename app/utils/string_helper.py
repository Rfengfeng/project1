from datetime import date, datetime
import random
import string


def generate_salt() -> str:
  # Generate a random salt
  return ''.join(random.choices(string.ascii_letters + string.digits, k=16))


def get_greeting() -> str:
  '''
  Get the appropriate greeting based on the time of day
  :return: The greeting
  '''
  now = datetime.now()
  if now.hour < 12:
    return 'Good morning'
  elif now.hour < 18:
    return 'Good afternoon'
  else:
    return 'Good evening'


def format_datetime(dt: datetime, fmt: str = '%d %b %Y %I:%M %p') -> str:
  '''
    Format a datetime object as a string
      :param dt: The datetime object to format
      :param fmt: The format string
      :return: The formatted string
  '''
  return dt.strftime(fmt)


def format_date(dt: datetime | date, fmt: str = '%d %b %Y') -> str:
  '''
    Format a date object as a string
      :param dt: The date object to format
      :param fmt: The format string
      :return: The formatted string
  '''
  return dt.strftime(fmt)


def format_time(dt: datetime, fmt: str = '%I:%M %p') -> str:
  '''
    Format a time object as a string
      :param dt: The time object to format
      :param fmt: The format string
      :return: The formatted string
  '''
  return dt.strftime(fmt)


def extract_user_address(user) -> str:
  '''
    Extract the address, suburb, and postcode from a user's address
      :param user: The user to extract the address from
      :return: A tuple of the address, suburb, and postcode
  '''
  arr = (user.address or '1234 Main St, Auckland 1010').replace(
      ', ', ',').split(',')
  if len(arr) < 2:
    arr.append('Auckland 1010')
  suburb_group = arr[1].strip().split(' ')
  postcode = suburb_group.pop()

  return (
      arr[0].strip(),
      ' '.join(suburb_group),
      postcode
  )
