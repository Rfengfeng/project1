"""Add profile pictures

Revision ID: 39c90ad9923c
Revises: 95a3130ebe40
Create Date: 2024-04-07 21:51:03.746908

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39c90ad9923c'
down_revision = '95a3130ebe40'
branch_labels = None
depends_on = None


def upgrade():
  # Add member picture
  op.execute('''
        INSERT INTO `image` (`title`, `path`, `size`)
        VALUES ('member', 'uploads/member.png', 371300)
    ''')

  image_id = op.get_bind().exec_driver_sql('''
        SELECT last_insert_id() as id
  ''').first()[0]

  op.execute(
      f"UPDATE `user` SET `profile_image_id` = {image_id} WHERE `email` = 'harry.potter@email.com'")

  # Add tutor picture
  op.execute('''
            INSERT INTO `image` (`title`, `path`, `size`)
            VALUES ('tutor', 'uploads/tutor.png', 143802)
        ''')

  image_id = op.get_bind().exec_driver_sql('''
          SELECT last_insert_id() as id
  ''').first()[0]
  op.execute(
      f"UPDATE `user` SET `profile_image_id` = {image_id} WHERE `email` = 'jane.doe@email.com'")

  # Add manager picture
  op.execute('''
    INSERT INTO `image` (`title`, `path`, `size`)
    VALUES ('manager', 'uploads/manager.png', 247353)
  ''')

  image_id = op.get_bind().exec_driver_sql('''
              SELECT last_insert_id() as id
      ''').first()[0]
  op.execute(
      f"UPDATE `user` SET `profile_image_id` = {image_id} WHERE `email` = 'john.smith@email.com'")

  pass


def downgrade():
  op.execute('''
      UPDATE `user` SET `profile_image_id` = null WHERE `email` IN (
          'harry.potter@email.com',
          'jane.doe@email.com',
          'john.smith@email.com'
      )
  ''')
  op.execute('''
        DELETE FROM `image` WHERE `title` IN ('member', 'tutor', 'manager')
  ''')

  pass
