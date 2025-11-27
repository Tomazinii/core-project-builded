"""add organization_type column

Revision ID: 6661ba7381bc
Revises: 8aae5c1a743e
Create Date: 2025-11-27 xx:xx:xx.xxxxxx
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '6661ba7381bc'
down_revision: Union[str, None] = '8aae5c1a743e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add organization_type column and enum type."""
    
    # 1. Cria o tipo enum apenas se não existir
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE organization_type AS ENUM ('PERSONAL', 'ENTERPRISE');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # 2. Adiciona a coluna (nullable temporariamente)
    op.add_column(
        'organizations',
        sa.Column('organization_type', sa.Enum('PERSONAL', 'ENTERPRISE', name='organization_type', create_type=False), nullable=True)
    )
    
    # 3. Define um valor padrão para registros existentes (se houver)
    op.execute("UPDATE organizations SET organization_type = 'ENTERPRISE' WHERE organization_type IS NULL")
    
    # 4. Torna a coluna NOT NULL
    op.alter_column('organizations', 'organization_type', nullable=False)
    
    # 5. Adiciona índice
    op.create_index('ix_organizations_organization_type', 'organizations', ['organization_type'], unique=False)


def downgrade() -> None:
    """Remove organization_type column."""
    op.drop_index('ix_organizations_organization_type', table_name='organizations')
    op.drop_column('organizations', 'organization_type')
    # Não remove o tipo enum no downgrade para não quebrar outras migrations