"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-11-09 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'denuncia',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('numero', sa.Integer(), nullable=False, unique=True),
        sa.Column('nombre', sa.String(length=100), nullable=False),
        sa.Column('lugar', sa.String(length=200), nullable=False),
    )

def downgrade():
    op.drop_table('denuncia')
