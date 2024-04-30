from datetime import datetime, timedelta
from flask import Blueprint, redirect, render_template, request, url_for, flash, abort
from app.database import db
from app.models.location import Location
from app.models.schedule import Schedule
from app.models.user import Role
from app.models.workshop import Workshop
from app.utils.session import require_login, require_roles
from sqlalchemy import or_

from app.utils.timetable import build_time_table

location_view = Blueprint('location_view', __name__)


@location_view.route('/locations', methods=['GET'])
@require_login()
def list_locations():
  '''
  List all locations
  '''
  page = request.args.get('page', 1, type=int)
  search_string = request.args.get('search_string', '')

  if search_string:
    search_term = f'%{search_string}%'
    query = db.session.query(Location).filter(
        or_(
            Location.title.ilike(search_term),
            Location.address1.ilike(search_term),
            Location.city.ilike(search_term),
            Location.state.ilike(search_term)
        )
    )
  else:
    query = db.session.query(Location)

  location_list = query.order_by(
      Location.title).paginate(page=page, per_page=10)

  return render_template('manager/locations_list.html', location_list=location_list)


@location_view.route('/locations/new', methods=['GET', 'POST'])
@require_roles([Role.manager])
def new_location():
  if request.method == 'POST':
    new_location = Location(
        title=request.form.get('title'),
        address1=request.form.get('address1'),
        address2=request.form.get('address2'),
        suburb=request.form.get('suburb'),
        city=request.form.get('city'),
        region=request.form.get('region'),
        state=request.form.get('state'),
        postcode=request.form.get('postcode')
    )
    db.session.add(new_location)
    db.session.commit()
    flash('Location added successfully!', 'success')
    return redirect(url_for('location_view.list_locations'))

  return render_template('location/edit.html', location=None)


@location_view.route('/locations/<int:id>/edit', methods=['GET', 'POST'])
@require_roles([Role.manager])
def edit_location(id):
  location = Location.query.get_or_404(id)
  if request.method == 'POST':
    # Update location details
    location.title = request.form.get('title')
    location.address1 = request.form.get('address1')
    location.address2 = request.form.get('address2')
    location.suburb = request.form.get('suburb')
    location.city = request.form.get('city')
    location.region = request.form.get('region')
    location.state = request.form.get('state')
    location.postcode = request.form.get('postcode')
    db.session.commit()
    flash('Location updated successfully!', 'success')
    return redirect(url_for('location_view.list_locations'))

  return render_template('location/edit.html', location=location)


@location_view.route('/locations/<int:id>/delete', methods=['POST'])
@require_roles([Role.manager])
def delete_location(id):

  location = Location.query.get_or_404(id)

  workshops = Workshop.query.filter_by(location_id=id).all()
  if workshops:
    flash('This location has booked workshops and cannot be removed.', 'danger')
    return redirect(url_for('location_view.list_locations'))

  db.session.delete(location)
  db.session.commit()
  flash('Location deleted successfully!', 'success')
  return redirect(url_for('location_view.list_locations'))


@location_view.route('/locations/<int:id>', methods=['GET'])
def view_location(id):
  month_offset = request.args.get('month_offset', 0, type=int)
  location = Location.query.get(id)
  if not location:
    flash('Location not found', 'danger')
    return redirect(url_for('homepage'))

  print(month_offset)

  start_of_month = datetime.today().replace(day=1)
  year_offset = 0
  new_month = start_of_month.month + month_offset
  if new_month > 12:
    year_offset = 1
    new_month = new_month - 12
  elif new_month < 1:
    year_offset = -1
    new_month = new_month + 12

  start_of_month = start_of_month.replace(
      month=new_month, year=start_of_month.year + year_offset)

  end_of_month = start_of_month.replace(
      month=start_of_month.month + 1) - timedelta(days=1)

  schedules = db.session.query(Schedule).filter(
      (Schedule.start_datetime >= start_of_month) & (
          Schedule.start_datetime <= end_of_month)
      & (Schedule.workshop.has(Workshop.location_id == id))
  ).all()
  print(schedules, start_of_month, end_of_month)

  table_entries = build_time_table(start_of_month, end_of_month, schedules)
  return render_template('location/view.html',
                         location=location,
                         table_entries=table_entries,
                         month_offset=month_offset)


@location_view.route('/locations/save', methods=['POST'])
@require_roles([Role.manager])
def save_location():
  location_id = request.form.get('id', type=int)
  if location_id:
    location = Location.query.get_or_404(location_id)
    action = "updated"
  else:
    location = Location()
    db.session.add(location)
    action = "added"

  location.title = request.form.get('title')
  location.address1 = request.form.get('address1')
  location.address2 = request.form.get('address2')
  location.suburb = request.form.get('suburb')
  location.city = request.form.get('city')
  location.region = request.form.get('region')
  location.state = request.form.get('state')
  location.postcode = request.form.get('postcode')
  location.facilities = request.form.get('facilities')

  db.session.commit()
  flash(f'Location {action} successfully!', 'success')
  return redirect(url_for('location_view.list_locations'))
