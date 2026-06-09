"""adicionar_campo_url_pdf_ordens_servico

Revision ID: ede5f0fbe2e0
Revises: 2b0308921206
Create Date: 2026-06-05 20:14:14.900023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ede5f0fbe2e0'
down_revision = '2b0308921206'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ordens_servico', sa.Column('url_pdf', sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column('ordens_servico', 'url_pdf')
