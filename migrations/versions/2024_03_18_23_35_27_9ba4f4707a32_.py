"""empty message

Revision ID: 9ba4f4707a32
Revises: 152d381f6eeb
Create Date: 2024-03-18 23:35:27.179749

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9ba4f4707a32'
down_revision = '152d381f6eeb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workshop_schedule_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('booking_ibfk_3', type_='foreignkey')
        batch_op.create_foreign_key(None, 'workshop_schedule', ['workshop_schedule_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.drop_column('workshop_id')

    with op.batch_alter_table('workshop_schedule', schema=None) as batch_op:
        batch_op.add_column(sa.Column('tutor_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'user', ['tutor_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('workshop_schedule', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('tutor_id')

    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('workshop_id', mysql.INTEGER(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('booking_ibfk_3', 'workshop', ['workshop_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
        batch_op.drop_column('workshop_schedule_id')

    # ### end Alembic commands ###
