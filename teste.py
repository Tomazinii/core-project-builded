# test_repository_manual.py
"""
Script para testar o OrganizationRepository manualmente
Execute: python test_repository_manual.py
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.domain.entities.organization import (
    Organization,
    OrganizationId,
    Slug,
    OrganizationType
)
from src.infrastructure.database.base import Base
from src.infrastructure.repository.organization_repository_impl import OrganizationRepositoryImpl


# =============================================================================
# CONFIGURAÇÃO
# =============================================================================

# URL do seu banco PostgreSQL
DATABASE_URL = "postgresql+asyncpg://myuser:mypassword@host.docker.internal:5434/mydatabase"


# =============================================================================
# SETUP
# =============================================================================

async def get_session():
    """Cria engine e session"""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    # Criar tabelas se não existirem
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = async_session()
    
    return session, engine


# =============================================================================
# TESTES MANUAIS
# =============================================================================

async def main():
    """Função principal para testar o repository"""
    
    print("=" * 70)
    print("🧪 TESTE MANUAL DO ORGANIZATION REPOSITORY")
    print("=" * 70)
    print()
    
    # 1. Criar session
    session, engine = await get_session()
    
    # 2. Instanciar o repository
    repository = OrganizationRepositoryImpl(session)
    
    print("✅ Repository instanciado com sucesso!")
    print(f"📦 Tipo: {type(repository)}")
    print()
    
    try:
        # =================================================================
        # TESTE 1: Criar uma organização
        # =================================================================
        print("=" * 70)
        print("1️⃣  TESTE: Criar organização")
        print("=" * 70)
        
        org = Organization(
            id=OrganizationId(),
            slug=Slug("minha-org-teste"),
            name="Minha Organização de Teste",
            type=OrganizationType.ENTERPRISE,
            logo=None,
            acl_id=None,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print(f"📝 Criando organização: {org.name}")
        print(f"   ID: {org.id.value}")
        print(f"   Slug: {org.slug.value}")
        
        await repository.save(org)
        await session.commit()
        
        print("✅ Organização salva com sucesso!")
        print()
        
        # =================================================================
        # TESTE 2: Buscar por ID
        # =================================================================
        print("=" * 70)
        print("2️⃣  TESTE: Buscar por ID")
        print("=" * 70)
        
        print(f"🔍 Buscando organização por ID: {org.id.value}")
        
        found = await repository.find_by_id(org.id)
        
        if found:
            print("✅ Organização encontrada!")
            print(f"   Nome: {found.name}")
            print(f"   Slug: {found.slug.value}")
            print(f"   Tipo: {found.type.value}")
        else:
            print("❌ Organização não encontrada")
        
        print()
        
        # =================================================================
        # TESTE 3: Buscar por slug
        # =================================================================
        print("=" * 70)
        print("3️⃣  TESTE: Buscar por slug")
        print("=" * 70)
        
        slug = Slug("minha-org-teste")
        print(f"🔍 Buscando organização por slug: {slug.value}")
        
        found_by_slug = await repository.find_by_slug(slug)
        
        if found_by_slug:
            print("✅ Organização encontrada!")
            print(f"   Nome: {found_by_slug.name}")
        else:
            print("❌ Organização não encontrada")
        
        print()
        
        # =================================================================
        # TESTE 4: Atualizar
        # =================================================================
        print("=" * 70)
        print("4️⃣  TESTE: Atualizar organização")
        print("=" * 70)
        
        org.name = "Nome Atualizado"
        print(f"📝 Atualizando nome para: {org.name}")
        
        await repository.save(org)
        await session.commit()
        
        # Buscar novamente para confirmar
        updated = await repository.find_by_id(org.id)
        print(f"✅ Nome após atualização: {updated.name}")
        print()
        
        # =================================================================
        # TESTE 5: Listar todas
        # =================================================================
        print("=" * 70)
        print("5️⃣  TESTE: Listar todas as organizações")
        print("=" * 70)
        
        all_orgs = await repository.list_all()
        print(f"📋 Total de organizações: {len(all_orgs)}")
        
        for i, o in enumerate(all_orgs, 1):
            print(f"   {i}. {o.name} ({o.slug.value})")
        
        print()
        
        # =================================================================
        # TESTE 6: Count
        # =================================================================
        print("=" * 70)
        print("6️⃣  TESTE: Contar organizações")
        print("=" * 70)
        
        total = await repository.count()
        print(f"🔢 Total de organizações: {total}")
        print()
        
        # =================================================================
        # TESTE 7: Exists
        # =================================================================
        print("=" * 70)
        print("7️⃣  TESTE: Verificar se existe")
        print("=" * 70)
        
        exists = await repository.exists(org.id)
        print(f"❓ Organização existe? {exists}")
        print()
        
        # =================================================================
        # TESTE 8: Delete
        # =================================================================
        print("=" * 70)
        print("8️⃣  TESTE: Deletar organização")
        print("=" * 70)
        
        print(f"🗑️  Deletando organização: {org.id.value}")
        
        deleted = await repository.delete(org.id)
        
        if deleted:
            await session.commit()
            print("✅ Organização deletada com sucesso!")
            
            # Verificar se realmente foi deletada
            exists_after = await repository.exists(org.id)
            print(f"❓ Ainda existe após deletar? {exists_after}")
        else:
            print("❌ Organização não encontrada para deletar")
        
        print()
        
        # =================================================================
        # TESTE 9: Get (deve lançar exceção se não encontrar)
        # =================================================================
        print("=" * 70)
        print("9️⃣  TESTE: Get (lança exceção se não encontrar)")
        print("=" * 70)
        
        try:
            print(f"🔍 Tentando get de organização deletada...")
            org_deleted = await repository.get_by_id(org.id)
            print(f"⚠️  Inesperado: Encontrou organização: {org_deleted.name}")
        except Exception as e:
            print(f"✅ Exceção lançada como esperado: {str(e)}")
        
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO")
        print("=" * 70)
        print(f"Tipo: {type(e).__name__}")
        print(f"Mensagem: {str(e)}")
        print()
        
        import traceback
        traceback.print_exc()
        
        await session.rollback()
    
    finally:
        # Limpar
        await session.close()
        await engine.dispose()
        
        print()
        print("=" * 70)
        print("🏁 FIM DOS TESTES")
        print("=" * 70)


# =============================================================================
# EXECUTAR
# =============================================================================

if __name__ == "__main__":
    asyncio.run(main())