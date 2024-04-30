# api
from app.blueprints.api.user import user_api
from app.blueprints.api.booking import booking_api
from app.blueprints.api.reminder import reminder_api

# views
from app.blueprints.view.user import user_view
from app.blueprints.view.lesson import lesson_view
from app.blueprints.view.booking import booking_view
from app.blueprints.view.manager import manager_view
from app.blueprints.view.subscription import subscription_view
from app.blueprints.view.member import member_view
from app.blueprints.view.tutor import tutor_view
from app.blueprints.view.payment import payment_view
from app.blueprints.view.track_payments import track_payments_view
from app.blueprints.view.schedule import schedule_view
from app.blueprints.view.location import location_view
from app.blueprints.view.news import news_view
from app.blueprints.view.report import report_view
