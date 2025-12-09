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
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=True),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('oauth_provider', sa.String(length=20), nullable=True),
    sa.Column('oauth_id', sa.String(length=255), nullable=True),
    sa.Column('avatar_url', sa.String(length=500), nullable=True),
    sa.Column('leetcode_username', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_leetcode_username'), 'users', ['leetcode_username'], unique=False)
    op.create_index(op.f('ix_users_oauth_id'), 'users', ['oauth_id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create solved_tasks table
    op.create_table('solved_tasks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('platform', sa.String(length=50), nullable=False),
    sa.Column('problem_id', sa.String(length=50), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('difficulty', sa.String(length=10), nullable=False),
    sa.Column('points', sa.Integer(), nullable=False),
    sa.Column('time_spent', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_solved_tasks_date'), 'solved_tasks', ['date'], unique=False)
    op.create_index(op.f('ix_solved_tasks_id'), 'solved_tasks', ['id'], unique=False)
    op.create_index(op.f('ix_solved_tasks_user_id'), 'solved_tasks', ['user_id'], unique=False)
    
    # Create month_goals table
    op.create_table('month_goals',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=False),
    sa.Column('month', sa.Integer(), nullable=False),
    sa.Column('target_xp', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_month_goals_id'), 'month_goals', ['id'], unique=False)
    op.create_index(op.f('ix_month_goals_user_id'), 'month_goals', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_month_goals_user_id'), table_name='month_goals')
    op.drop_index(op.f('ix_month_goals_id'), table_name='month_goals')
    op.drop_table('month_goals')
    
    op.drop_index(op.f('ix_solved_tasks_user_id'), table_name='solved_tasks')
    op.drop_index(op.f('ix_solved_tasks_id'), table_name='solved_tasks')
    op.drop_index(op.f('ix_solved_tasks_date'), table_name='solved_tasks')
    op.drop_table('solved_tasks')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_oauth_id'), table_name='users')
    op.drop_index(op.f('ix_users_leetcode_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
