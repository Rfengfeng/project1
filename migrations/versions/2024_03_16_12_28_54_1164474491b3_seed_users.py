"""Seed users

Revision ID: 1164474491b3
Revises: a417abf9e220
Create Date: 2024-03-16 12:28:54.820360

"""
from alembic import op
import sqlalchemy as sa

from app.models.user import Role
from app.utils.string_helper import generate_salt
from flask_hashing import Hashing


# revision identifiers, used by Alembic.
revision = '1164474491b3'
down_revision = 'a417abf9e220'
branch_labels = None
depends_on = None

hashing = Hashing()


def upgrade():
  salt1 = generate_salt()
  salt2 = generate_salt()
  salt3 = generate_salt()

  user_table = sa.sql.table(
      'user',
      sa.Column('role', sa.String),
      sa.Column('first_name', sa.String),
      sa.Column('last_name', sa.String),
      sa.Column('email', sa.String),
      sa.Column('salt', sa.String),
      sa.Column('password', sa.String)
  )
  op.bulk_insert(user_table,
                 [
                     {
                         'role': Role.manager.value,
                         'first_name': 'John',
                         'last_name': 'Smith',
                         'email': 'john.smith@email.com',
                         'salt': salt1,
                         'password': hashing.hash_value('password', salt=salt1)
                     },
                     {
                         'role': Role.tutor.value,
                         'first_name': 'Jane',
                         'last_name': 'Doe',
                         'email': 'jane.doe@email.com',
                         'salt': salt2,
                         'password': hashing.hash_value('password', salt=salt2)
                     },
                     {
                         'role': Role.member.value,
                         'first_name': 'Harry',
                         'last_name': 'Potter',
                         'email': 'harry.potter@email.com',
                         'salt': salt3,
                         'password': hashing.hash_value('password', salt=salt3)
                     }
                 ])


def downgrade():
  # delete users by email
  # op.execute('DELETE FROM user WHERE email IN (%s, %s, %s)', (
  #     'john.smith@email.com',
  #     'jane.doe@email.com',
  #     'harry.potter@email.com',
  # ))
  table = sa.sql.table('user', sa.sql.column('email', sa.String))
  op.execute(
      table
      .delete()
      .where(table.c.email.in_([
          'john.smith@email.com',
          'jane.doe@email.com',
          'harry.potter@email.com',
      ]))
  )
