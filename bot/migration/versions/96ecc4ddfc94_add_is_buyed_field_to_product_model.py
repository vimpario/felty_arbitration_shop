"""Add is_buyed field to Product model

Revision ID: 96ecc4ddfc94
Revises: 3ab6cd69f120
Create Date: 2025-01-06 07:13:21.426969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '96ecc4ddfc94'
down_revision: Union[str, None] = '3ab6cd69f120'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('is_buyed', sa.Boolean(), nullable=False, server_default='false'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('products', 'is_buyed')
    # ### end Alembic commands ###
