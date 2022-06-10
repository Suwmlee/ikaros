"""Add srcfolder

Revision ID: 6749dee88757
Revises: 67cbdd6413c3
Create Date: 2021-12-21 12:37:44.402694

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6749dee88757'
down_revision = '67cbdd6413c3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transrecords', schema=None) as batch_op:
        batch_op.add_column(sa.Column('srcfolder', sa.String(), nullable=True))
        batch_op.drop_column('success')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('transrecords', schema=None) as batch_op:
        batch_op.add_column(sa.Column('success', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('srcfolder')

    # ### end Alembic commands ###