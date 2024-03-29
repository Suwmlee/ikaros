"""Add refresh url for transfer

Revision ID: ef9c9dbb8a8e
Revises: c6d3cfb805e7
Create Date: 2021-08-21 12:39:01.825614

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ef9c9dbb8a8e'
down_revision = 'c6d3cfb805e7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.drop_column('auto_exit')
        batch_op.drop_column('soft_link')
        batch_op.drop_column('debug_info')

    with op.batch_alter_table('transferconfigs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('refresh_url', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transferconfigs', schema=None) as batch_op:
        batch_op.drop_column('refresh_url')

    with op.batch_alter_table('settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('debug_info', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('soft_link', sa.BOOLEAN(), nullable=True))
        batch_op.add_column(sa.Column('auto_exit', sa.BOOLEAN(), nullable=True))

    # ### end Alembic commands ###
