from datetime import datetime, timedelta


def build_time_table(date_from: datetime, date_to: datetime, table_entries: list) -> list:
  today = datetime.now()
  table_contents = []
  # 1. Get the first Monday
  first_monday = date_from - timedelta(days=date_from.weekday())
  last_sunday = date_to + timedelta(days=6 - date_to.weekday())
  entries_by_date = {}
  for entry in table_entries:
    entries = entries_by_date.get(entry.start_datetime.date(), [])
    entries.append(entry)
    entries_by_date[entry.start_datetime.date()] = entries

  # 2. Build the table
  for i in range((last_sunday - first_monday).days + 1):
    day = first_monday + timedelta(days=i)
    day_entries = entries_by_date.get(day.date(), [])
    table_contents.append({
        'date': day,
        'entries': day_entries,
        'is_today': day.date() == today.date(),
        'is_weekend': day.weekday() in [5, 6],
        'is_in_month': day.month == date_from.month
    })

  return table_contents


def build_time_table_of_this_month(table_entries: list) -> list:
  # build a time table of a whole month with the given entries
  # table_entries: list of entries
  # returns: a list of lists with the time table

  # date from is monday of this week
  date_from = datetime.now() - timedelta(days=datetime.now().weekday())
  date_to = date_from.replace(month=date_from.month + 1) - timedelta(days=1)
  return build_time_table(date_from, date_to, table_entries)
