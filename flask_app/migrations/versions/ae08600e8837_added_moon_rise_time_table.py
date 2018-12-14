"""added moon_rise_time table

Revision ID: ae08600e8837
Revises: 15ab7696fb24
Create Date: 2018-12-14 10:02:27.223207

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae08600e8837'
down_revision = '15ab7696fb24'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('moon_rise_time',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_at', sa.DateTime(), nullable=False),
    sa.Column('moon_phase_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('start_at')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('moon_rise_time')
    # ### end Alembic commands ###