"""add_leetcode_username_to_users

Revision ID: ed721a9614c3
Revises: 
Create Date: 2025-11-26 17:43:04.766067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed721a9614c3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add leetcode_username column to users table
    op.add_column('users', sa.Column('leetcode_username', sa.String(length=100), nullable=True))
    op.create_index(op.f('ix_users_leetcode_username'), 'users', ['leetcode_username'], unique=False)


def downgrade() -> None:
    # Remove leetcode_username column from users table
    op.drop_index(op.f('ix_users_leetcode_username'), table_name='users')
    op.drop_column('users', 'leetcode_username')
