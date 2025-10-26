"""initial

Revision ID: 001
Revises:
Create Date: 2024-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_created_at', 'users', ['created_at'])

    # Create stocks table
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('symbol', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('sector', sa.String(), nullable=True),
        sa.Column('industry', sa.String(), nullable=True),
        sa.Column('market_cap', sa.Float(), nullable=True),
        sa.Column('last_price', sa.Float(), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )
    op.create_index('ix_stocks_sector', 'stocks', ['sector'])
    op.create_index('ix_stocks_industry', 'stocks', ['industry'])
    op.create_index('ix_stocks_last_updated', 'stocks', ['last_updated'])
    op.create_index('ix_stocks_sector_industry', 'stocks', ['sector', 'industry'])

    # Create portfolios table
    op.create_table(
        'portfolios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('last_updated', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_portfolios_user_id', 'portfolios', ['user_id'])
    op.create_index('ix_portfolios_user_created', 'portfolios', ['user_id', 'created_at'])
    op.create_index('ix_portfolios_last_updated', 'portfolios', ['last_updated'])

    # Create stock_portfolio association table
    op.create_table(
        'stock_portfolio',
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('stock_id', 'portfolio_id')
    )
    op.create_index('ix_stock_portfolio_stock_id', 'stock_portfolio', ['stock_id'])
    op.create_index('ix_stock_portfolio_portfolio_id', 'stock_portfolio', ['portfolio_id'])

    # Create portfolio_weights table
    op.create_table(
        'portfolio_weights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('portfolio_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_portfolio_weights_portfolio_id', 'portfolio_weights', ['portfolio_id'])
    op.create_index('ix_portfolio_weights_stock_id', 'portfolio_weights', ['stock_id'])
    op.create_index('ix_portfolio_weights_portfolio_stock', 'portfolio_weights', ['portfolio_id', 'stock_id'])
    op.create_index('ix_portfolio_weights_last_updated', 'portfolio_weights', ['last_updated'])

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('report_type', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reports_user_id', 'reports', ['user_id'])
    op.create_index('ix_reports_stock_id', 'reports', ['stock_id'])
    op.create_index('ix_reports_report_type', 'reports', ['report_type'])
    op.create_index('ix_reports_user_created', 'reports', ['user_id', 'created_at'])
    op.create_index('ix_reports_stock_type', 'reports', ['stock_id', 'report_type'])

    # Create backups table
    op.create_table(
        'backups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('size', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, default=sa.func.now()),
        sa.Column('status', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_backups_status', 'backups', ['status'])
    op.create_index('ix_backups_created_status', 'backups', ['created_at', 'status'])

def downgrade():
    op.drop_table('backups')
    op.drop_table('reports')
    op.drop_table('portfolio_weights')
    op.drop_table('stock_portfolio')
    op.drop_table('portfolios')
    op.drop_table('stocks')
    op.drop_table('users')