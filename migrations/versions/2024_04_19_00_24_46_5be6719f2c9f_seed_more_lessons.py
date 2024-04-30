"""Seed more lessons

Revision ID: 5be6719f2c9f
Revises: a993f879b2ea
Create Date: 2024-04-19 00:24:46.776265

"""
from operator import le
import random
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5be6719f2c9f'
down_revision = 'a993f879b2ea'
branch_labels = None
depends_on = None


def upgrade():
  user_table = sa.sql.table(
      'user',
      sa.Column('id', sa.Integer),
      sa.Column('email', sa.String),
      sa.Column('role', sa.String)
  )
  tutors = op.get_bind().execute(
      user_table.select().where(user_table.c.role == 'tutor')
  ).fetchall()

  lesson_table = sa.sql.table(
      'lesson',
      sa.Column('title', sa.String),
      sa.Column('cost', sa.DECIMAL(10, 2)),
      sa.Column('lesson_number', sa.String),
      sa.Column('description', sa.String),
      sa.Column('tutor_id', sa.Integer)
  )

  lessons = [
      {
          "title": "Introduction to Merino Wool",
          "lesson_number": "MRN101",
          "cost": 100.00,
          "description": "This introductory lesson provides an overview of the history, characteristics, and benefits of merino wool. Participants will learn about the unique properties of merino wool fibers and their applications in various industries, including fashion, outdoor apparel, and textiles."
      },
      {
          "title": "Merino Wool Processing Techniques",
          "lesson_number": "MRN102",
          "cost": 150.00,
          "description": "Explore the intricate processes involved in transforming raw merino wool into high-quality yarns and fabrics. This lesson covers shearing, sorting, scouring, carding, spinning, and weaving techniques used in merino wool processing, along with the importance of quality control measures."
      },
      {
          "title": "Merino Sheep Breeding Fundamentals",
          "lesson_number": "MRN103",
          "cost": 120.00,
          "description": "Delve into the fundamentals of merino sheep breeding, including genetic selection, mating systems, and reproductive management practices. Participants will gain insights into breeding objectives, performance recording, and the use of modern technologies to enhance merino sheep productivity and wool quality."
      },
      {
          "title": "Advanced Merino Wool Quality Control",
          "lesson_number": "MRN104",
          "cost": 180.00,
          "description": "This advanced lesson focuses on quality control measures throughout the merino wool production chain. Topics include fiber testing methods, standards compliance, traceability systems, and sustainable practices to ensure consistent quality and meet consumer demands."
      },
      {
          "title": "Merino Wool Dyeing and Finishing",
          "lesson_number": "MRN105",
          "cost": 90.00,
          "description": "Gain insights into the art and science of dyeing and finishing merino wool textiles. Participants will learn about dye types, colorfastness properties, dyeing techniques, and environmentally friendly finishing processes to create vibrant and durable merino wool products."
      },
      {
          "title": "Sustainable Merino Farming Practices",
          "lesson_number": "MRN106",
          "cost": 200.00,
          "description": "Explore sustainable farming practices tailored to merino sheep production systems. This lesson covers pasture management, water conservation, biodiversity preservation, animal welfare standards, and eco-friendly solutions to minimize environmental impact and maximize farm profitability."
      },
      {
          "title": "Merino Wool Marketing Strategies",
          "lesson_number": "MRN107",
          "cost": 70.00,
          "description": "Discover effective marketing strategies to promote merino wool products in domestic and international markets. Topics include brand positioning, target audience analysis, digital marketing tactics, storytelling techniques, and collaboration opportunities within the merino wool industry."
      },
      {
          "title": "Merino Wool Fabric Innovation",
          "lesson_number": "MRN108",
          "cost": 110.00,
          "description": "Stay abreast of the latest innovations in merino wool fabric development and applications. From performance textiles for outdoor adventures to luxurious fabrics for high-end fashion, this lesson showcases cutting-edge technologies, design trends, and consumer preferences driving fabric innovation."
      },
      {
          "title": "Merino Wool Fashion Trends",
          "lesson_number": "MRN109",
          "cost": 130.00,
          "description": "Explore current and emerging fashion trends featuring merino wool as a versatile and sustainable textile choice. Participants will gain insights into runway looks, celebrity endorsements, consumer preferences, and market forecasts shaping the future of merino wool fashion."
      },
      {
          "title": "Merino Wool in Outdoor Apparel",
          "lesson_number": "MRN110",
          "cost": 160.00,
          "description": "Discover the performance benefits of merino wool in outdoor apparel design and construction. From moisture-wicking baselayers to insulating midlayers and durable outerwear, this lesson highlights the natural properties of merino wool that make it an ideal choice for adventurers and athletes."
      }
  ]
  for lesson in lessons:
    # get a random tutor
    index = random.randint(0, len(tutors) - 1)
    tutor_id = tutors[index][0]
    lesson['tutor_id'] = tutor_id

  op.bulk_insert(lesson_table, lessons)


def downgrade():
  # no need to remove seeded
  pass
