"""Seed location_data and workshops

Revision ID: 25cb48f7327a
Revises: 5be6719f2c9f
Create Date: 2024-04-19 00:39:28.926266

"""
import random
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25cb48f7327a'
down_revision = '5be6719f2c9f'
branch_labels = None
depends_on = None


def upgrade():
  location_data = [
      {
          "title": "Auckland CBD",
          "address1": "12 Main Street",
          "address2": "Apt. 3",
          "suburb": "Albany",
          "region": "Auckland",
          "postcode": "0110"
      },
      {
          "title": "Hamilton Central",
          "address1": "45 Queen Street",
          "address2": "Unit 8",
          "suburb": "Hamilton",
          "region": "Waikato",
          "postcode": "3200"
      },
      {
          "title": "Wellington CBD",
          "address1": "7 Park Avenue",
          "address2": "Suite 15",
          "suburb": "Wellington",
          "region": "Wellington",
          "postcode": "6011"
      },
      {
          "title": "Christchurch Central",
          "address1": "28 High Street",
          "address2": "Apt. 10",
          "suburb": "Christchurch",
          "region": "Canterbury",
          "postcode": "8011"
      },
      {
          "title": "Auckland Central",
          "address1": "50 Church Road",
          "address2": "Unit 6",
          "suburb": "Auckland",
          "region": "Auckland",
          "postcode": "1010"
      }
  ]

  location_table = sa.sql.table(
      'location',
      sa.Column('id', sa.Integer),
      sa.Column('address1', sa.String),
      sa.Column('address2', sa.String),
      sa.Column('suburb', sa.String),
      sa.Column('region', sa.String),
      sa.Column('postcode', sa.String)
  )
  op.bulk_insert(location_table, location_data)

  locations = op.get_bind().execute(
      location_table.select()
  ).fetchall()

  workshops = [
      {
          "title": "Merino Wool Spinning Workshop",
          "description": "Learn the art of spinning merino wool fibers into yarns of various thicknesses and textures. This hands-on workshop covers basic spinning techniques, fiber preparation, wheel maintenance, and creative yarn design. Suitable for beginners and intermediate spinners.",
          "price": 50.00
      },
      {
          "title": "Merino Wool Dyeing Masterclass",
          "description": "Unlock the secrets of dyeing merino wool to create stunning and unique colorways. Explore different dyeing methods such as hand painting, immersion dyeing, and resist techniques. Participants will experiment with color mixing, color theory, and safe dye handling practices.",
          "price": 120.00
      },
      {
          "title": "Needle Felting with Merino Wool",
          "description": "Discover the therapeutic art of needle felting using soft and luxurious merino wool roving. In this workshop, participants will learn needle felting basics, including shaping, sculpting, and detailing techniques. Create adorable felted creatures, ornaments, and embellishments.",
          "price": 80.00
      },
      {
          "title": "Merino Wool Knitting Retreat",
          "description": "Immerse yourself in a weekend of knitting bliss with merino wool as your muse. This retreat offers a relaxed and supportive environment for knitters of all skill levels. Enjoy workshops on advanced knitting techniques, pattern customization, and garment finishing. Indulge in yarn shopping, delicious meals, and cozy fireside chats.",
          "price": 180.00
      },
      {
          "title": "Wet Felting Merino Wool Hats",
          "description": "Create one-of-a-kind felted hats using the wet felting technique and luxurious merino wool fibers. This workshop covers hat design principles, template making, and felting methods to achieve seamless and well-fitting hats. Participants will leave with a finished felted hat ready to wear or gift.",
          "price": 150.00
      }
  ]

  for workshop in workshops:
    index = random.randint(0, len(locations) - 1)
    workshop['location_id'] = locations[index][0]

  workshop_table = sa.sql.table(
      'workshop',
      sa.Column('title', sa.String),
      sa.Column('description', sa.String),
      sa.Column('price', sa.DECIMAL(10, 2)),
      sa.Column('location_id', sa.Integer)
  )

  op.bulk_insert(
      workshop_table,
      workshops
  )


def downgrade():
  pass
