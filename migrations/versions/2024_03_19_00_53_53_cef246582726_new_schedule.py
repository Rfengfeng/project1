"""New Schedule

Revision ID: cef246582726
Revises: f16db2e8842f
Create Date: 2024-03-19 00:53:53.988946

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cef246582726'
down_revision = 'f16db2e8842f'
branch_labels = None
depends_on = None


def upgrade():
  op.create_table('schedule',
                  sa.Column('id', sa.Integer(),
                            autoincrement=True, nullable=False),
                  sa.Column('start_datetime', sa.DateTime(), nullable=True),
                  sa.Column('end_datetime', sa.DateTime(), nullable=True),
                  sa.Column('cost', sa.Numeric(
                      precision=8, scale=2), nullable=False, server_default='0.00'),
                  sa.Column('lesson_id', sa.Integer(), nullable=True),
                  sa.Column('workshop_id', sa.Integer(), nullable=True),
                  sa.Column('tutor_id', sa.Integer(), nullable=True),
                  sa.ForeignKeyConstraint(
                      ['lesson_id'], ['lesson.id'], ondelete='CASCADE', onupdate='CASCADE'),
                  sa.ForeignKeyConstraint(['tutor_id'], ['user.id'],
                                          ondelete='CASCADE', onupdate='CASCADE'),
                  sa.ForeignKeyConstraint(
                      ['workshop_id'], ['workshop.id'], ondelete='CASCADE', onupdate='CASCADE'),
                  sa.PrimaryKeyConstraint('id')
                  )
  # Define the lesson_schedule table
  # Copy data from lesson_schedule table
  op.execute("""
        INSERT INTO schedule (lesson_id, start_datetime, end_datetime, cost)
        SELECT lesson_id, start_datetime, end_datetime, cost
        FROM lesson_schedule
  """)

  op.execute("""
    UPDATE `schedule` s INNER JOIN lesson l ON l.id = s.lesson_id
    SET s.tutor_id = l.tutor_id
  """)

  # Copy data from workshop_schedule table
  op.execute("""
        INSERT INTO schedule (workshop_id, start_datetime, end_datetime, tutor_id)
        SELECT workshop_id, start_datetime, end_datetime, tutor_id
        FROM workshop_schedule
  """)


def downgrade():
  op.drop_table('schedule')
