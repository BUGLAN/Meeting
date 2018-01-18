"""empty message

Revision ID: f91eeaf93a9a
Revises: 3148108d8ad3
Create Date: 2018-01-17 12:07:26.218615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f91eeaf93a9a'
down_revision = '3148108d8ad3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('name', table_name='meet')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('name', 'meet', ['name'], unique=True)
    # ### end Alembic commands ###