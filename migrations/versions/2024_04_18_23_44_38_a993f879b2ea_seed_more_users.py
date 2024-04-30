"""Seed more users

Revision ID: a993f879b2ea
Revises: 76bf068dd527
Create Date: 2024-04-18 23:44:38.348107

"""
from alembic import op
import sqlalchemy as sa

from app.utils.hash import generate_password_hash
from app.utils.string_helper import generate_salt


# revision identifiers, used by Alembic.
revision = 'a993f879b2ea'
down_revision = '76bf068dd527'
branch_labels = None
depends_on = None


def upgrade():
  user_table = sa.table('user',
                        sa.column('first_name', sa.String),
                        sa.column('last_name', sa.String),
                        sa.column('email', sa.String),
                        sa.column('date_of_birth', sa.Date),
                        sa.column('role', sa.String),
                        sa.column('title', sa.String),
                        sa.column('position', sa.String),
                        sa.column('address', sa.String),
                        sa.column('years_of_experience', sa.Integer),
                        sa.column('qualification', sa.String),
                        sa.column('introduction', sa.String),
                        sa.column('password', sa.String),
                        sa.column('salt', sa.String),
                        sa.column('active', sa.Boolean),
                        )
  manager = {
      'first_name': 'Alice', 'last_name': 'Smith', 'email': 'alice.smith@email.com',
      'date_of_birth': '1990-01-01', 'role': 'manager', 'title': 'Ms', 'position': 'Manager',
      'address': '1234 Main St, Auckland 1010',
  }
  manager['salt'] = generate_salt()
  manager['password'] = generate_password_hash(
      'pp_merino_123!', manager['salt'])
  manager['active'] = True
  op.bulk_insert(user_table, [manager])

  tutors = [
      {
          "first_name": "John",
          "last_name": "Doe",
          "email": "john.doe@email.com",
          "date_of_birth": "1985-06-15",
          "title": "Mr.",
          "position": "Senior Tutor",
          "years_of_experience": 10,
          "qualification": "Master's Degree in Education",
          "introduction": "I have been a tutor for over 10 years, specializing in helping students achieve academic success."
      },
      {
          "first_name": "Jane",
          "last_name": "Smith",
          "email": "jane.smith@email.com",
          "date_of_birth": "1992-11-20",
          "title": "Ms.",
          "position": "Junior Tutor",
          "years_of_experience": 5,
          "qualification": "Bachelor's Degree in Mathematics",
          "introduction": "I am passionate about helping students improve their math skills and build a strong foundation in the subject."
      },
      {
          "first_name": "Michael",
          "last_name": "Johnson",
          "email": "michael.johnson@email.com",
          "date_of_birth": "1978-03-12",
          "title": "Dr.",
          "position": "Head Tutor",
          "years_of_experience": 15,
          "qualification": "Ph.D. in Educational Psychology",
          "introduction": "With over 15 years of experience in education, I am dedicated to helping students reach their full potential and achieve academic excellence."
      },
      {
          "first_name": "Emily",
          "last_name": "Davis",
          "email": "emily.davis@email.com",
          "date_of_birth": "1990-09-05",
          "title": "Ms.",
          "position": "Tutor",
          "years_of_experience": 3,
          "qualification": "Bachelor's Degree in English Literature",
          "introduction": "I'm an enthusiastic tutor who loves helping students improve their reading and writing skills."
      }
  ]
  for tutor in tutors:
    tutor['salt'] = generate_salt()
    tutor['password'] = generate_password_hash('pp_merino_123!', tutor['salt'])
    tutor['role'] = 'tutor'
    tutor['active'] = True
  op.bulk_insert(user_table, tutors)

  members = [
      {
          "first_name": "Emma",
          "last_name": "Smith",
          "email": "emma.smith@email.com",
          "date_of_birth": "1990-05-15",
          "title": "Mrs.",
          "position": "Merino Specialist",
          "address": "Maple Street, Auckland 1010, New Zealand"
      },
      {
          "first_name": "Liam",
          "last_name": "Johnson",
          "email": "liam.johnson@email.com",
          "date_of_birth": "1985-08-23",
          "title": "Mr.",
          "position": "Farmer",
          "address": "Cedar Street, Wellington 5000, New Zealand"
      },
      {
          "first_name": "Olivia",
          "last_name": "Williams",
          "email": "olivia.williams@email.com",
          "date_of_birth": "1993-02-10",
          "title": "Ms.",
          "position": "Merino Wool Trader",
          "address": "Elm Street, Christchurch 9000, New Zealand"
      },
      {
          "first_name": "Noah",
          "last_name": "Jones",
          "email": "noah.jones@email.com",
          "date_of_birth": "1988-11-30",
          "title": "Dr.",
          "position": "Student",
          "address": "Pine Street, Hamilton 3200, New Zealand"
      },
      {
          "first_name": "Ava",
          "last_name": "Brown",
          "email": "ava.brown@email.com",
          "date_of_birth": "1995-06-18",
          "title": "Mrs.",
          "position": "Merino Breeder",
          "address": "Birch Street, Tauranga 3100, New Zealand"
      },
      {
          "first_name": "Lucas",
          "last_name": "Davis",
          "email": "lucas.davis@email.com",
          "date_of_birth": "1992-09-05",
          "title": "Mr.",
          "position": "Merino Specialist",
          "address": "Spruce Street, Dunedin 9010, New Zealand"
      },
      {
          "first_name": "Sophia",
          "last_name": "Miller",
          "email": "sophia.miller@email.com",
          "date_of_birth": "1986-04-27",
          "title": "Ms.",
          "position": "Merino Wool Processor",
          "address": "Willow Street, Palmerston North 4410, New Zealand"
      },
      {
          "first_name": "Mason",
          "last_name": "Wilson",
          "email": "mason.wilson@email.com",
          "date_of_birth": "1991-07-11",
          "title": "Mr.",
          "position": "Farmer",
          "address": "Oak Street, Napier 4104, New Zealand"
      },
      {
          "first_name": "Isabella",
          "last_name": "Moore",
          "email": "isabella.moore@email.com",
          "date_of_birth": "1989-03-20",
          "title": "Mrs.",
          "position": "Merino Specialist",
          "address": "Main Street, Hastings 4120, New Zealand"
      },
      {
          "first_name": "Ethan",
          "last_name": "Taylor",
          "email": "ethan.taylor@email.com",
          "date_of_birth": "1994-10-08",
          "title": "Dr.",
          "position": "Student",
          "address": "Ash Street, New Plymouth 4100, New Zealand"
      },
      {
          "first_name": "Amelia",
          "last_name": "Anderson",
          "email": "amelia.anderson@email.com",
          "date_of_birth": "1987-12-25",
          "title": "Mrs.",
          "position": "Merino Wool Trader",
          "address": "Maple Street, Auckland 1040, New Zealand"
      },
      {
          "first_name": "Logan",
          "last_name": "Thomas",
          "email": "logan.thomas@email.com",
          "date_of_birth": "1990-02-14",
          "title": "Mr.",
          "position": "Farmer",
          "address": "Cedar Street, Wellington 5300, New Zealand"
      },
      {
          "first_name": "Mia",
          "last_name": "Jackson",
          "email": "mia.jackson@email.com",
          "date_of_birth": "1984-06-30",
          "title": "Ms.",
          "position": "Merino Breeder",
          "address": "Elm Street, Christchurch 9100, New Zealand"
      },
      {
          "first_name": "Elijah",
          "last_name": "White",
          "email": "elijah.white@email.com",
          "date_of_birth": "1993-09-12",
          "title": "Dr.",
          "position": "Merino Specialist",
          "address": "Pine Street, Hamilton, New Zealand"
      },
      {
          "first_name": "Harper",
          "last_name": "Harris",
          "email": "harper.harris@email.com",
          "date_of_birth": "1988-05-05",
          "title": "Mrs.",
          "position": "Student",
          "address": "Birch Street, Tauranga 4200, New Zealand"
      },
      {
          "first_name": "James",
          "last_name": "Martin",
          "email": "james.martin@email.com",
          "date_of_birth": "1992-01-17",
          "title": "Mr.",
          "position": "Merino Wool Processor",
          "address": "Spruce Street, Dunedin 9001, New Zealand"
      },
      {
          "first_name": "Evelyn",
          "last_name": "Thompson",
          "email": "evelyn.thompson@email.com",
          "date_of_birth": "1985-08-03",
          "title": "Ms.",
          "position": "Farmer",
          "address": "Willow Street, Palmerston North 4100, New Zealand"
      },
      {
          "first_name": "Alexander",
          "last_name": "Garcia",
          "email": "alexander.garcia@email.com",
          "date_of_birth": "1991-04-21",
          "title": "Mr.",
          "position": "Merino Specialist",
          "address": "Oak Street, Napier 4200, New Zealand"
      },
      {
          "first_name": "Charlotte",
          "last_name": "Martinez",
          "email": "charlotte.martinez@email.com",
          "date_of_birth": "1989-10-10",
          "title": "Mrs.",
          "position": "Merino Wool Trader",
          "address": "Main Street, Hastings 4100, New Zealand"
      },
      {
          "first_name": "Michael",
          "last_name": "Robinson",
          "email": "michael.robinson@email.com",
          "date_of_birth": "1994-03-25",
          "title": "Dr.",
          "position": "Merino Breeder",
          "address": "Ash Street, New Plymouth 4000, New Zealand"
      }
  ]

  for member in members:
    member['salt'] = generate_salt()
    member['password'] = generate_password_hash(
        'pp_merino_123!', member['salt'])
    member['role'] = 'member'
    member['active'] = True
  op.bulk_insert(user_table, members)


def downgrade():
  pass  # No need to remove the seed data
