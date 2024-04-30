"""fix schedules

Revision ID: d2cfdc2cd69b
Revises: 60386b321635
Create Date: 2024-03-22 23:14:36.549867

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2cfdc2cd69b'
down_revision = '60386b321635'
branch_labels = None
depends_on = None


def upgrade():
  op.execute('''
    UPDATE booking b
    INNER JOIN lesson_schedule ls
    ON ls.id = b.lesson_schedule_id
    INNER JOIN lesson ON lesson.id = ls.lesson_id
    INNER JOIN schedule s on s.lesson_id = lesson.id
      AND b.start_datetime = s.start_datetime
    SET b.schedule_id = s.id
  ''')

  op.execute('''
    UPDATE booking b
    INNER JOIN workshop_schedule ws
    ON ws.id = b.workshop_schedule_id
    INNER JOIN workshop ON workshop.id = ws.workshop_id
    INNER JOIN schedule s on s.workshop_id = workshop.id
      AND b.start_datetime = s.start_datetime
    SET b.schedule_id = s.id
  ''')


def downgrade():
  op.execute('''
    UPDATE booking b
    INNER JOIN lesson_schedule ls
    ON ls.id = b.lesson_schedule_id
    INNER JOIN lesson ON lesson.id = ls.lesson_id
    INNER JOIN schedule s on s.lesson_id = lesson.id
    SET b.schedule_id = s.id
  ''')

  op.execute('''
    UPDATE booking b
    INNER JOIN workshop_schedule ws
    ON ws.id = b.workshop_schedule_id
    INNER JOIN workshop ON workshop.id = ws.workshop_id
    INNER JOIN schedule s on s.workshop_id = workshop.id
    SET b.schedule_id = s.id
  ''')
