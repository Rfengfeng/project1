from datetime import datetime
from multiprocessing import reduction
import re
from flask import Blueprint, redirect, render_template, request, url_for, flash
from app.database import db
from app.models.news import News
from app.models.user import Role
from app.utils.session import get_current_user, require_login, require_roles


news_view = Blueprint('news_view', __name__)


@news_view.route('/')
@require_login()
def list_news():
  '''
  List all the news
  '''

  # Pagination and search
  page = request.args.get('page', 1, type=int)
  search_string = request.args.get('search_string', None)

  query = db.session.query(News)
  if search_string:
    query = query.filter(
        News.title.ilike(f'%{search_string}%')
    )

  news = query.order_by(
      News.published_at.desc()
  ).paginate(page=page, per_page=10)

  return render_template('news/list.html', news_list=news)


@news_view.route('/<int:id>', methods=['GET'])
@require_login()
def view_news(id):
  '''
  View a news
  '''
  news = db.session.query(News).get(id)
  if not news:
    flash('News not found', 'danger')
    return redirect(url_for('news_view.list_news'))
  return render_template('news/view.html', news=news, page_title=news.title)


@news_view.route('/<int:id>/edit', methods=['GET'])
@require_roles([Role.manager])
def edit_news(id):
  '''
  Show the edit form for a news
  '''
  news = db.session.query(News).get(id)
  if not news:
    flash('News not found', 'danger')
    return redirect(url_for('news_view.list_news'))

  return render_template('news/edit.html', news=news, page_title=news.title)


@news_view.route('/new', methods=['GET'])
@require_roles([Role.manager])
def new_news():
  '''
  Show the form to add a news
  '''
  return render_template('news/edit.html', page_title='Add News')


@news_view.route('/', methods=['POST'], defaults={'id': None})
@news_view.route('/<int:id>', methods=['POST'])
@require_roles([Role.manager])
def save_news(id):
  '''
  Save the news
  Create a new news if the id is None
  Otherwise, update the news
  '''

  current_user = get_current_user()
  if id:
    # Check if the news exists
    news = db.session.query(News).get(id)
    if not news:
      flash('News not found', 'danger')
      return redirect(url_for('manger_view.list_news'))
  else:
    # Create a new news
    news = News()
    news.published_at = datetime.now()
    news.user_id = current_user.id

  # Save the news
  news.title = request.form.get('title')
  news.content = request.form.get('content')
  news.author = request.form.get('author')

  if not id:
    db.session.add(news)
  else:
    db.session.merge(news)
  db.session.commit()
  flash('News saved', 'success')
  return redirect(url_for('manager_view.list_news'))


@news_view.route('/<int:id>/delete', methods=['POST'])
@require_roles([Role.manager])
def delete_news(id):
  '''
  Delete a news
  '''
  news = db.session.query(News).get(id)
  if not news:
    flash('News not found', 'danger')
    return redirect(url_for('manager_view.list_news'))

  db.session.delete(news)
  db.session.commit()
  flash('News deleted', 'success')
  return redirect(url_for('manager_view.list_news'))
