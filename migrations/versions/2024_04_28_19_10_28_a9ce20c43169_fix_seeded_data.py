"""Fix seeded data

Revision ID: a9ce20c43169
Revises: 579fea817aca
Create Date: 2024-04-28 19:10:28.792356

"""
from alembic import op
import sqlalchemy as sa

from app.utils.hash import generate_password_hash
from app.utils.string_helper import generate_salt


# revision identifiers, used by Alembic.
revision = 'a9ce20c43169'
down_revision = '579fea817aca'
branch_labels = None
depends_on = None


def upgrade():
  # Fix some lesson schedules were assigned to the wrong tutor
  op.execute("""
        UPDATE `schedule` INNER JOIN `lesson` ON `schedule`.`lesson_id` = `lesson`.`id`
        SET `schedule`.`tutor_id` = `lesson`.`tutor_id`
               """)
  # Update the users to use strong passwords
  emails_to_update = [
      'john.smith@email.com',
      'jane.doe@email.com',
      'harry.potter@email.com',
  ]
  strong_password = 'pp_merino_123!'

  for email in emails_to_update:
    salt = generate_salt()
    password_hash = generate_password_hash(strong_password, salt)
    op.execute(f"""
        UPDATE `user` SET `password` = '{password_hash}', `salt` = '{salt}'
        WHERE `email` = '{email}'
    """)


def downgrade():
  pass
