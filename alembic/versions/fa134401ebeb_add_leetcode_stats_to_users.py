"""add_leetcode_stats_to_users

Revision ID: fa134401ebeb
Revises: ed721a9614c3
Create Date: 2025-12-10 19:15:22.123456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa134401ebeb'
down_revision: Union[str, None] = 'ed721a9614c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('ranking', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('reputation', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('total_solved', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('easy_solved', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('medium_solved', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('hard_solved', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_synced_at')
    op.drop_column('users', 'hard_solved')
    op.drop_column('users', 'medium_solved')
    op.drop_column('users', 'easy_solved')
    op.drop_column('users', 'total_solved')
    op.drop_column('users', 'reputation')
    op.drop_column('users', 'ranking')
