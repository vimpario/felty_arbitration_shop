"""Updated payment_id field in Purchase model

Revision ID: a916ce90673a
Revises: 48d179003461
Create Date: 2025-01-16 19:49:31.117705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a916ce90673a'
down_revision: Union[str, None] = '48d179003461'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###