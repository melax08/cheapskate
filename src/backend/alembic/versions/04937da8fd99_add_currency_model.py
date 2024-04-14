"""Add currency model

Revision ID: 04937da8fd99
Revises: e47f7c87fabb
Create Date: 2024-03-13 20:52:06.116340

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04937da8fd99'
down_revision: Union[str, None] = 'e47f7c87fabb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('currency',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('letter_code', sa.String(length=3), nullable=False),
    sa.Column('country', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('country'),
    sa.UniqueConstraint('letter_code'),
    sa.UniqueConstraint('name')
    )
    op.add_column('expense', sa.Column('currency_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'expense', 'currency', ['currency_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'expense', type_='foreignkey')
    op.drop_column('expense', 'currency_id')
    op.drop_table('currency')
    # ### end Alembic commands ###
