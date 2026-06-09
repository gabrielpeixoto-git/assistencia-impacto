"""adicionar_campo_cor_usuario

Revision ID: 2b0308921206
Revises: 003_add_token_acesso_publico
Create Date: 2026-06-05 20:08:27.632988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b0308921206'
down_revision = '003_add_token_acesso_publico'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('usuarios', sa.Column('cor', sa.String(7), nullable=False, server_default='#6C63FF'))


def downgrade() -> None:
    op.drop_column('usuarios', 'cor')
