"""empty message

Revision ID: c60d318b4486
Revises: d135dffe7af9
Create Date: 2019-08-05 16:51:22.142712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c60d318b4486'
down_revision = 'd135dffe7af9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('app', sa.Column('api_key', sa.String(length=1000), nullable=True))
    op.add_column('app', sa.Column('refresh_api_key', sa.String(length=1000), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('app', 'refresh_api_key')
    op.drop_column('app', 'api_key')
    # ### end Alembic commands ###
