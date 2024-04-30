
from app.models import Schedule, location
from app.database import db
from app.models.workshop import Workshop


def exist_overlap(start_datetime, end_datetime, tutor_id=0, location_id=0, current_schedule_id=0):
  '''check if a period between the start_datetime and end_datetime overlaps with
  any existing lesson schedule or workshop schedule run by a specific tutor.
    :param start_datetime: start datetime of the period
    :param end_datetime: end datetime of the period
    :param tutor_id: tutor id
    :param workshop_id: workshop id
    :param current_schedule_id: current schedule id
    :return: True if there is an overlap, False otherwise
  '''

  # Filter the schedules by the start and end datetime
  filters = (Schedule.id != current_schedule_id) & (
      (
          (Schedule.start_datetime >= start_datetime) & (Schedule.start_datetime < end_datetime))
      |
      (
          (Schedule.end_datetime >= start_datetime) & (Schedule.end_datetime < end_datetime))
      |
      (
          (start_datetime <= Schedule.start_datetime) & (
              end_datetime > Schedule.end_datetime)
      )
  )

  tutor_conflicts_filters = None  # A filter to check if the tutor is already booked
  # A filter to check if the location is already booked
  location_conflicts_filters = None

  if (tutor_id):
    tutor_conflicts_filters = (Schedule.tutor_id == tutor_id)

  if (location_id):
    location_conflicts_filters = (
        Schedule.workshop.has(Workshop.location_id == location_id))

  # Combine the filters
  if (tutor_conflicts_filters is not None) and (location_conflicts_filters is not None):
    filters &= (tutor_conflicts_filters | location_conflicts_filters)
  elif tutor_conflicts_filters is not None:
    filters &= tutor_conflicts_filters
  elif location_conflicts_filters is not None:
    filters &= location_conflicts_filters

  # Get the schedules that overlap with the given period
  overlapped_schedules = db.session.query(Schedule).filter(filters)

  return overlapped_schedules.first() != None
