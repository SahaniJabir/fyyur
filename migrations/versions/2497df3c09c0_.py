"""empty message

Revision ID: 2497df3c09c0
Revises: ac68df660945
Create Date: 2020-07-11 23:27:14.942771

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2497df3c09c0'
down_revision = 'ac68df660945'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Show')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('Venue_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('Artist_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('start_time', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['Artist_id'], ['Artist.id'], name='Show_Artist_id_fkey'),
    sa.ForeignKeyConstraint(['Venue_id'], ['Venue.id'], name='Show_Venue_id_fkey')
    )
    # ### end Alembic commands ###
