"""News user id

Revision ID: a508955bfe3f
Revises: aab1d8b56c4f
Create Date: 2024-04-14 21:44:55.368783

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a508955bfe3f'
down_revision = '349814d20430'
branch_labels = None
depends_on = None


def upgrade():
  manager = op.get_bind().exec_driver_sql(
      'SELECT id FROM `user` WHERE `role` = \'manager\' LIMIT 1').first()

  with op.batch_alter_table('news') as batch_op:
    batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))

  op.execute(f'UPDATE news SET user_id = {manager.id}')

  with op.batch_alter_table('news') as batch_op:
    batch_op.create_foreign_key('fk_news_user_id', 'user', ['user_id'], ['id'])
    batch_op.alter_column('subject', existing_type=sa.String(
        255), nullable=False, new_column_name='title')

    batch_op.alter_column('publish_at', existing_type=sa.DateTime(
    ), new_column_name='published_at', nullable=False, server_default=sa.text('NOW()'))


def downgrade():
  with op.batch_alter_table('news') as batch_op:
    batch_op.drop_constraint('fk_news_user_id', type_='foreignkey')
    batch_op.drop_column('user_id')
    batch_op.alter_column('title', existing_type=sa.String(
        255), nullable=True, new_column_name='subject')
    batch_op.alter_column('published_at', existing_type=sa.DateTime(
    ), new_column_name='publish_at', nullable=True, server_default=None)
