"""
Script de seed completo para o sistema Assistência Impacto.
Popula o banco de dados com dados de demonstração realistas.
Execute com: python seed.py
"""
import asyncio
import random
from datetime import datetime, timedelta, date, UTC
from decimal import Decimal
import uuid
from zoneinfo import ZoneInfo

# Import dos models e database session do projeto
from app.database import AsyncSessionLocal
from app.models.usuario import Usuario, Perfil
from app.models.cliente import Cliente, TipoCliente, TipoDocumento
from app.models.categoria_servico import CategoriaServico
from app.models.ordem_servico import (
    OrdemServico, StatusOS, PrioridadeOS,
    ItemOrdemServico, ChecklistOrdemServico, StatusPagamento
)
from app.models.orcamento import Orcamento, ItemOrcamento, StatusOrcamento
from app.models.agenda import Agenda, TipoEvento, StatusEvento
from app.models.financeiro import Transacao, CategoriaFinanceira, TipoTransacao, StatusTransacao
from app.models.estoque import ItemEstoque, CategoriaEstoque, Unidade
from app.models.configuracao import Configuracao
from app.core.seguranca import hash_senha
from sqlalchemy import select

# Timezone BRT
BRT = ZoneInfo("America/Sao_Paulo")


async def get_session():
    """Obtém sessão do banco de dados."""
    async with AsyncSessionLocal() as session:
        yield session


async def seed_usuarios(session: AsyncSessionLocal):
    """Cria usuários do sistema (idempotente)."""
    print("Criando usuários...")
    
    usuarios_data = [
        {
            "email": "admin@assistenciaimpacto.com.br",
            "senha": "admin123",
            "nome_completo": "Administrador do Sistema",
            "perfil": Perfil.ADMIN,
            "verificado": True,
            "ativo": True
        },
        {
            "email": "joao@assistenciaimpacto.com.br",
            "senha": "Tecnico@123",
            "nome_completo": "João Silva",
            "perfil": Perfil.TECNICO,
            "verificado": True,
            "ativo": True,
            "telefone": "(11) 98765-4321"
        },
        {
            "email": "maria@assistenciaimpacto.com.br",
            "senha": "Tecnico@123",
            "nome_completo": "Maria Santos",
            "perfil": Perfil.TECNICO,
            "verificado": True,
            "ativo": True,
            "telefone": "(11) 98765-4322"
        },
        {
            "email": "carlos@assistenciaimpacto.com.br",
            "senha": "Tecnico@123",
            "nome_completo": "Carlos Oliveira",
            "perfil": Perfil.TECNICO,
            "verificado": True,
            "ativo": True,
            "telefone": "(11) 98765-4323"
        }
    ]
    
    usuarios_criados = {}
    for usuario_data in usuarios_data:
        result = await session.execute(
            select(Usuario).where(Usuario.email == usuario_data["email"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            senha_hash = hash_senha(usuario_data.pop("senha"))
            usuario = Usuario(**usuario_data, senha_hash=senha_hash)
            session.add(usuario)
            await session.flush()
            usuarios_criados[usuario_data["email"]] = usuario
            print(f"  ✓ Criado: {usuario_data['email']}")
        else:
            usuarios_criados[usuario_data["email"]] = existing
            print(f"  - Já existe: {usuario_data['email']}")
    
    await session.commit()
    return usuarios_criados


async def seed_categorias_servico(session: AsyncSessionLocal):
    """Cria categorias de serviço (idempotente)."""
    print("Criando categorias de serviço...")
    
    categorias_data = [
        {"nome": "Hidráulica", "icone": "droplet", "cor": "#3B82F6", "preco_min": 80.0, "preco_max": 400.0},
        {"nome": "Elétrica", "icone": "zap", "cor": "#EAB308", "preco_min": 100.0, "preco_max": 600.0},
        {"nome": "Alvenaria", "icone": "layers", "cor": "#F97316", "preco_min": 150.0, "preco_max": 2000.0},
        {"nome": "Pintura", "icone": "paintbrush", "cor": "#8B5CF6", "preco_min": 200.0, "preco_max": 3000.0},
        {"nome": "Serralheria", "icone": "wrench", "cor": "#6B7280", "preco_min": 100.0, "preco_max": 800.0},
        {"nome": "Vidraçaria", "icone": "square", "cor": "#06B6D4", "preco_min": 150.0, "preco_max": 1500.0},
        {"nome": "Marcenaria", "icone": "hammer", "cor": "#F59E0B", "preco_min": 200.0, "preco_max": 2500.0},
        {"nome": "Ar Condicionado", "icone": "wind", "cor": "#60A5FA", "preco_min": 150.0, "preco_max": 800.0},
        {"nome": "Informática", "icone": "monitor", "cor": "#10B981", "preco_min": 80.0, "preco_max": 500.0},
        {"nome": "Limpeza", "icone": "sparkles", "cor": "#14B8A6", "preco_min": 150.0, "preco_max": 1200.0}
    ]
    
    categorias_criadas = {}
    for cat_data in categorias_data:
        result = await session.execute(
            select(CategoriaServico).where(CategoriaServico.nome == cat_data["nome"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            categoria = CategoriaServico(
                nome=cat_data["nome"],
                descricao=f"Serviços de {cat_data['nome']}",
                icone=cat_data["icone"],
                cor=cat_data["cor"],
                duracao_padrao_minutos=random.randint(60, 180),
                preco_minimo=cat_data["preco_min"],
                preco_maximo=cat_data["preco_max"]
            )
            session.add(categoria)
            await session.flush()
            categorias_criadas[cat_data["nome"]] = categoria
            print(f"  ✓ Criado: {cat_data['nome']}")
        else:
            categorias_criadas[cat_data["nome"]] = existing
            print(f"  - Já existe: {cat_data['nome']}")
    
    await session.commit()
    return categorias_criadas


async def seed_categorias_estoque(session: AsyncSessionLocal):
    """Cria categorias de estoque (idempotente)."""
    print("Criando categorias de estoque...")
    
    categorias_data = [
        {"nome": "Tubos e Conexões", "cor": "#3B82F6", "icone": "droplet"},
        {"nome": "Fios e Cabos", "cor": "#EAB308", "icone": "zap"},
        {"nome": "Ferramentas", "cor": "#6B7280", "icone": "wrench"},
        {"nome": "Tintas e Acabamentos", "cor": "#8B5CF6", "icone": "paintbrush"},
        {"nome": "Vidros", "cor": "#06B6D4", "icone": "square"},
        {"nome": "Madeira", "cor": "#F59E0B", "icone": "hammer"},
        {"nome": "Elétricos", "cor": "#60A5FA", "icone": "zap"},
        {"nome": "Eletrônicos", "cor": "#10B981", "icone": "monitor"},
        {"nome": "Limpeza", "cor": "#14B8A6", "icone": "sparkles"},
        {"nome": "Outros", "cor": "#9CA3AF", "icone": "box"}
    ]
    
    categorias_criadas = {}
    for cat_data in categorias_data:
        result = await session.execute(
            select(CategoriaEstoque).where(CategoriaEstoque.nome == cat_data["nome"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            categoria = CategoriaEstoque(**cat_data)
            session.add(categoria)
            await session.flush()
            categorias_criadas[cat_data["nome"]] = categoria
            print(f"  ✓ Criado: {cat_data['nome']}")
        else:
            categorias_criadas[cat_data["nome"]] = existing
            print(f"  - Já existe: {cat_data['nome']}")
    
    await session.commit()
    return categorias_criadas


async def seed_categorias_financeiras(session: AsyncSessionLocal):
    """Cria categorias financeiras (idempotente)."""
    print("Criando categorias financeiras...")
    
    categorias_data = [
        # Receitas
        {"nome": "Serviços Prestados", "tipo": TipoTransacao.RECEITA, "cor": "#10B981", "icone": "dollar-sign"},
        {"nome": "Venda de Materiais", "tipo": TipoTransacao.RECEITA, "cor": "#10B981", "icone": "shopping-cart"},
        # Despesas
        {"nome": "Materiais", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "box"},
        {"nome": "Aluguel", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "home"},
        {"nome": "Combustível", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "fuel"},
        {"nome": "Equipamentos", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "tool"},
        {"nome": "Alimentação", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "utensils"},
        {"nome": "Impostos", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "file-text"},
        {"nome": "Manutenção Veículos", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "car"},
        {"nome": "Marketing", "tipo": TipoTransacao.DESPESA, "cor": "#EF4444", "icone": "megaphone"}
    ]
    
    categorias_criadas = {}
    for cat_data in categorias_data:
        result = await session.execute(
            select(CategoriaFinanceira).where(CategoriaFinanceira.nome == cat_data["nome"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            categoria = CategoriaFinanceira(**cat_data)
            session.add(categoria)
            await session.flush()
            categorias_criadas[cat_data["nome"]] = categoria
            print(f"  ✓ Criado: {cat_data['nome']}")
        else:
            categorias_criadas[cat_data["nome"]] = existing
            print(f"  - Já existe: {cat_data['nome']}")
    
    await session.commit()
    return categorias_criadas


async def seed_configuracoes(session: AsyncSessionLocal, admin_id: str):
    """Cria configurações padrão do sistema (idempotente)."""
    print("Criando configurações padrão...")
    
    configuracoes_data = [
        # Dados da Empresa
        {"chave": "nome_empresa", "valor": "Assistência Impacto Soluções", "descricao": "Nome da empresa"},
        {"chave": "cnpj_empresa", "valor": "00.000.000/0000-00", "descricao": "CNPJ da empresa"},
        {"chave": "telefone_empresa", "valor": "(11) 3456-7890", "descricao": "Telefone da empresa"},
        {"chave": "email_empresa", "valor": "contato@assistenciaimpacto.com.br", "descricao": "Email da empresa"},
        {"chave": "endereco_empresa", "valor": "Rua Exemplo, 123 - Centro - São Paulo/SP", "descricao": "Endereço da empresa"},
        
        # Configurações de Email
        {"chave": "smtp_host", "valor": "smtp.gmail.com", "descricao": "Host SMTP"},
        {"chave": "smtp_porta", "valor": "587", "descricao": "Porta SMTP"},
        {"chave": "smtp_usuario", "valor": "", "descricao": "Usuário SMTP"},
        {"chave": "email_remetente", "valor": "noreply@assistenciaimpacto.com.br", "descricao": "Email remetente"},
        {"chave": "nome_remetente", "valor": "Assistência Impacto", "descricao": "Nome remetente"},
        
        # Configurações de WhatsApp
        {"chave": "evolution_api_url", "valor": "", "descricao": "URL da API Evolution"},
        {"chave": "whatsapp_telefone", "valor": "(11) 98765-4321", "descricao": "Telefone WhatsApp"},
        
        # APIs Externas
        {"chave": "viacep_api_url", "valor": "https://viacep.com.br/ws/", "descricao": "URL da API ViaCEP"},
        
        # Frontend
        {"chave": "url_frontend", "valor": "http://localhost:5173", "descricao": "URL do frontend"},
        
        # Ambiente
        {"chave": "ambiente", "valor": "desenvolvimento", "descricao": "Ambiente do sistema"},
        {"chave": "permitir_registro_publico", "valor": "true", "descricao": "Permitir registro público"},
        
        # Uploads
        {"chave": "tamanho_maximo_upload_mb", "valor": "10", "descricao": "Tamanho máximo de upload em MB"},
        {"chave": "tipos_imagem_permitidos", "valor": "jpg,jpeg,png,webp", "descricao": "Tipos de imagem permitidos"},
        
        # Preferências de Notificação
        {"chave": "notif_nova_os", "valor": "true", "descricao": "Notificar nova OS"},
        {"chave": "notif_orcamento_aprovado", "valor": "true", "descricao": "Notificar orçamento aprovado"},
        {"chave": "notif_orcamento_rejeitado", "valor": "true", "descricao": "Notificar orçamento rejeitado"},
        {"chave": "notif_agendamento_proximo", "valor": "true", "descricao": "Notificar agendamento próximo"},
        {"chave": "notif_estoque_baixo", "valor": "true", "descricao": "Notificar estoque baixo"},
        {"chave": "notif_relatorio_semanal", "valor": "false", "descricao": "Notificar relatório semanal"},
        {"chave": "notif_canal_email", "valor": "true", "descricao": "Canal de notificação: email"},
        {"chave": "notif_canal_sistema", "valor": "true", "descricao": "Canal de notificação: sistema"},
        {"chave": "notif_frequencia", "valor": "imediato", "descricao": "Frequência de notificação"},
        
        # Preferências de Aparência
        {"chave": "tema_dark_mode", "valor": "false", "descricao": "Tema dark mode"},
        {"chave": "tema_cor_primaria", "valor": "#6C63FF", "descricao": "Cor primária do tema"},
        {"chave": "tema_densidade", "valor": "normal", "descricao": "Densidade do tema"},
        
        # Configurações Regionais
        {"chave": "regiao_moeda", "valor": "BRL", "descricao": "Moeda da região"},
        {"chave": "regiao_fuso_horario", "valor": "America/Sao_Paulo", "descricao": "Fuso horário"},
        {"chave": "regiao_formato_data", "valor": "DD/MM/AAAA", "descricao": "Formato de data"},
        {"chave": "regiao_idioma", "valor": "pt-BR", "descricao": "Idioma"}
    ]
    
    configuracoes_criadas = []
    for config_data in configuracoes_data:
        result = await session.execute(
            select(Configuracao).where(Configuracao.chave == config_data["chave"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            config = Configuracao(
                chave=config_data["chave"],
                valor=config_data["valor"],
                descricao=config_data["descricao"],
                atualizado_por=admin_id
            )
            session.add(config)
            await session.flush()
            configuracoes_criadas.append(config)
            print(f"  ✓ Criado: {config_data['chave']}")
        else:
            configuracoes_criadas.append(existing)
            print(f"  - Já existe: {config_data['chave']}")
    
    await session.commit()
    return configuracoes_criadas


async def seed_clientes(session: AsyncSessionLocal, admin_id: str):
    """Cria 20 clientes realistas (idempotente)."""
    print("Criando clientes...")
    
    clientes_data = [
        # Residenciais (CPF)
        {"nome": "Ana Paula Costa", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "São Paulo", "telefone": "(11) 98765-4321", "whatsapp": "(11) 98765-4321"},
        {"nome": "Roberto Mendes", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Campinas", "telefone": "(19) 97654-3210", "whatsapp": "(19) 97654-3210"},
        {"nome": "Fernanda Lima", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Santo André", "telefone": "(11) 96543-2109", "whatsapp": "(11) 96543-2109"},
        {"nome": "Carlos Eduardo Souza", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Osasco", "telefone": "(11) 95432-1098", "whatsapp": "(11) 95432-1098"},
        {"nome": "Juliana Martins", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Guarulhos", "telefone": "(11) 94321-0987", "whatsapp": "(11) 94321-0987"},
        {"nome": "Ricardo Alves", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Mauá", "telefone": "(11) 93210-9876", "whatsapp": "(11) 93210-9876"},
        {"nome": "Patricia Ferreira", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "São Paulo", "telefone": "(11) 92109-8765", "whatsapp": "(11) 92109-8765"},
        {"nome": "Luiz Antonio", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Ribeirão Preto", "telefone": "(16) 98765-4321", "whatsapp": "(16) 98765-4321"},
        {"nome": "Mariana Silva", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Campinas", "telefone": "(19) 97654-3211", "whatsapp": "(19) 97654-3211"},
        {"nome": "Felipe Gomes", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "São Paulo", "telefone": "(11) 96543-2108", "whatsapp": "(11) 96543-2108"},
        {"nome": "Carla Rodrigues", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Santo André", "telefone": "(11) 95432-1097", "whatsapp": "(11) 95432-1097"},
        {"nome": "Paulo Henrique", "tipo": TipoCliente.RESIDENCIAL, "doc_tipo": TipoDocumento.CPF, "cidade": "Osasco", "telefone": "(11) 94321-0986", "whatsapp": "(11) 94321-0986"},
        # Comerciais (CNPJ)
        {"nome": "Empresa ABC Ltda", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "Guarulhos", "telefone": "(11) 3456-7890", "whatsapp": "(11) 98765-0001"},
        {"nome": "Tech Solutions EIRELI", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "São Paulo", "telefone": "(11) 2345-6789", "whatsapp": "(11) 98765-0002"},
        {"nome": "Comércio Centro Ltda", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "Mauá", "telefone": "(11) 4567-8901", "whatsapp": "(11) 98765-0003"},
        {"nome": "Indústria Metalúrgica SA", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "Santo André", "telefone": "(11) 5678-9012", "whatsapp": "(11) 98765-0004"},
        {"nome": "Restaurante Sabor Caseiro", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "Campinas", "telefone": "(19) 3456-7890", "whatsapp": "(19) 98765-0005"},
        {"nome": "Hotel Pousada Descanso", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "Ribeirão Preto", "telefone": "(16) 3456-7890", "whatsapp": "(16) 98765-0006"},
        {"nome": "Supermercado Preço Bom", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "Osasco", "telefone": "(11) 6789-0123", "whatsapp": "(11) 98765-0007"},
        {"nome": "Farmácia Saúde Total", "tipo": TipoCliente.COMERCIAL, "doc_tipo": TipoDocumento.CNPJ, "cidade": "São Paulo", "telefone": "(11) 7890-1234", "whatsapp": "(11) 98765-0008"}
    ]
    
    clientes_criados = []
    for cliente_data in clientes_data:
        result = await session.execute(
            select(Cliente).where(Cliente.nome == cliente_data["nome"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            cliente = Cliente(
                nome=cliente_data["nome"],
                email=f"{cliente_data['nome'].lower().replace(' ', '.')}@email.com",
                telefone=cliente_data["telefone"],
                whatsapp=cliente_data["whatsapp"],
                tipo_documento=cliente_data["doc_tipo"],
                numero_documento=f"{'0' * 11 if cliente_data['doc_tipo'] == TipoDocumento.CPF else '0' * 14}",
                tipo_cliente=cliente_data["tipo"],
                logradouro=random.choice(["Rua", "Avenida", "Travessa"]),
                numero=str(random.randint(1, 9999)),
                bairro=random.choice(["Centro", "Jardim América", "Vila Mariana", "Pinheiros", "Mooca"]),
                cidade=cliente_data["cidade"],
                estado="SP",
                cep=f"{random.randint(10000, 99999)}-{random.randint(100, 999)}",
                avaliacao=random.randint(3, 5),
                ativo=True,
                criado_por=admin_id
            )
            session.add(cliente)
            await session.flush()
            clientes_criados.append(cliente)
            print(f"  ✓ Criado: {cliente_data['nome']}")
        else:
            clientes_criados.append(existing)
            print(f"  - Já existe: {cliente_data['nome']}")
    
    await session.commit()
    return clientes_criados


async def seed_itens_estoque(session: AsyncSessionLocal, categorias_estoque: dict):
    """Cria 30 itens de estoque (idempotente)."""
    print("Criando itens de estoque...")
    
    itens_data = [
        {"sku": "CANO-PVC-3/4", "nome": "Cano PVC 3/4\"", "categoria": "Tubos e Conexões", "unidade": Unidade.UNIDADE, "estoque": 25, "min": 10, "max": 50, "custo": 8.50, "venda": 15.00},
        {"sku": "FIO-ELETRICO-2.5", "nome": "Fio Elétrico 2.5mm (rolo 50m)", "categoria": "Fios e Cabos", "unidade": Unidade.ROLO, "estoque": 8, "min": 5, "max": 20, "custo": 89.00, "venda": 150.00},
        {"sku": "TINTA-BRANCA-3.6L", "nome": "Tinta Branca 3.6L", "categoria": "Tintas e Acabamentos", "unidade": Unidade.UNIDADE, "estoque": 3, "min": 5, "max": 15, "custo": 45.00, "venda": 80.00},
        {"sku": "CHAVE-PHILLIPS", "nome": "Chave de Fenda Phillips", "categoria": "Ferramentas", "unidade": Unidade.UNIDADE, "estoque": 12, "min": 3, "max": 20, "custo": 15.00, "venda": 30.00},
        {"sku": "DISJUNTOR-20A", "nome": "Disjuntor 20A", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 2, "min": 5, "max": 30, "custo": 28.00, "venda": 55.00},
        {"sku": "VEDACAO-SILICONE", "nome": "Vedação Silicone 280ml", "categoria": "Outros", "unidade": Unidade.UNIDADE, "estoque": 15, "min": 8, "max": 40, "custo": 18.50, "venda": 35.00},
        {"sku": "CANO-PVC-1/2", "nome": "Cano PVC 1/2\"", "categoria": "Tubos e Conexões", "unidade": Unidade.UNIDADE, "estoque": 40, "min": 15, "max": 60, "custo": 6.50, "venda": 12.00},
        {"sku": "CONEXAO-T", "nome": "Conexão T PVC", "categoria": "Tubos e Conexões", "unidade": Unidade.UNIDADE, "estoque": 30, "min": 10, "max": 50, "custo": 5.00, "venda": 10.00},
        {"sku": "FIO-ELETRICO-4.0", "nome": "Fio Elétrico 4.0mm (rolo 50m)", "categoria": "Fios e Cabos", "unidade": Unidade.ROLO, "estoque": 6, "min": 5, "max": 15, "custo": 120.00, "venda": 200.00},
        {"sku": "TINTA-CINZA-3.6L", "nome": "Tinta Cinza 3.6L", "categoria": "Tintas e Acabamentos", "unidade": Unidade.UNIDADE, "estoque": 8, "min": 5, "max": 15, "custo": 48.00, "venda": 85.00},
        {"sku": "ALICATE-UNIVERSAL", "nome": "Alicate Universal", "categoria": "Ferramentas", "unidade": Unidade.UNIDADE, "estoque": 10, "min": 3, "max": 15, "custo": 35.00, "venda": 65.00},
        {"sku": "TOMADA-2P", "nome": "Tomada 2P+T 10A", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 25, "min": 10, "max": 50, "custo": 8.00, "venda": 15.00},
        {"sku": "VIDRO-TEMPERADO", "nome": "Vidro Temperado 8mm", "categoria": "Vidros", "unidade": Unidade.UNIDADE, "estoque": 5, "min": 3, "max": 10, "custo": 150.00, "venda": 300.00},
        {"sku": "MADEIRA-PINHO", "nome": "Madeira Pinho 2x3m", "categoria": "Madeira", "unidade": Unidade.METRO, "estoque": 20, "min": 10, "max": 40, "custo": 45.00, "venda": 90.00},
        {"sku": "FITA-ISOLANTE", "nome": "Fita Isolante 20m", "categoria": "Fios e Cabos", "unidade": Unidade.UNIDADE, "estoque": 35, "min": 15, "max": 60, "custo": 4.50, "venda": 10.00},
        {"sku": "ROSETA-PLASTICA", "nome": "Roseta Plástica", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 50, "min": 20, "max": 80, "custo": 2.00, "venda": 5.00},
        {"sku": "TINTA-PRETA-3.6L", "nome": "Tinta Preta 3.6L", "categoria": "Tintas e Acabamentos", "unidade": Unidade.UNIDADE, "estoque": 6, "min": 5, "max": 15, "custo": 50.00, "venda": 90.00},
        {"sku": "MARTELO", "nome": "Martelo Profissional", "categoria": "Ferramentas", "unidade": Unidade.UNIDADE, "estoque": 8, "min": 3, "max": 12, "custo": 45.00, "venda": 85.00},
        {"sku": "LAMPADA-LED-9W", "nome": "Lâmpada LED 9W", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 40, "min": 20, "max": 100, "custo": 12.00, "venda": 25.00},
        {"sku": "CIMENTO-50KG", "nome": "Cimento 50kg", "categoria": "Outros", "unidade": Unidade.UNIDADE, "estoque": 15, "min": 5, "max": 30, "custo": 32.00, "venda": 55.00},
        {"sku": "AREIA-M3", "nome": "Areia Média m³", "categoria": "Outros", "unidade": Unidade.METRO, "estoque": 10, "min": 3, "max": 20, "custo": 80.00, "venda": 150.00},
        {"sku": "CHAVE-FENDA", "nome": "Chave de Fenda", "categoria": "Ferramentas", "unidade": Unidade.UNIDADE, "estoque": 15, "min": 5, "max": 25, "custo": 12.00, "venda": 25.00},
        {"sku": "CAIXA-EMENDA", "nome": "Caixa de Emenda 100x100x50", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 20, "min": 10, "max": 40, "custo": 15.00, "venda": 30.00},
        {"sku": "TUBO-CONDUITE", "nome": "Tubo Conduite 20mm", "categoria": "Fios e Cabos", "unidade": Unidade.METRO, "estoque": 45, "min": 20, "max": 80, "custo": 6.00, "venda": 12.00},
        {"sku": "ESPARDAPELE", "nome": "Espadraple 50m", "categoria": "Tintas e Acabamentos", "unidade": Unidade.UNIDADE, "estoque": 12, "min": 5, "max": 20, "custo": 25.00, "venda": 50.00},
        {"sku": "SERRA-COPA", "nome": "Serra Copa 127mm", "categoria": "Ferramentas", "unidade": Unidade.UNIDADE, "estoque": 5, "min": 2, "max": 10, "custo": 85.00, "venda": 150.00},
        {"sku": "INTERRUPTOR-SIMPLES", "nome": "Interruptor Simples", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 30, "min": 15, "max": 60, "custo": 7.00, "venda": 14.00},
        {"sku": "COLA-BRANCA", "nome": "Cola Branca 500g", "categoria": "Outros", "unidade": Unidade.UNIDADE, "estoque": 18, "min": 8, "max": 30, "custo": 18.00, "venda": 35.00},
        {"sku": "FURADEIRA-IMPACTO", "nome": "Furadeira de Impacto", "categoria": "Ferramentas", "unidade": Unidade.UNIDADE, "estoque": 3, "min": 1, "max": 5, "custo": 280.00, "venda": 450.00},
        {"sku": "REATOR-T8", "nome": "Reator T8 Eletrônico", "categoria": "Elétricos", "unidade": Unidade.UNIDADE, "estoque": 14, "min": 5, "max": 25, "custo": 35.00, "venda": 65.00}
    ]
    
    itens_criados = []
    for item_data in itens_data:
        result = await session.execute(
            select(ItemEstoque).where(ItemEstoque.sku == item_data["sku"])
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            categoria = categorias_estoque[item_data["categoria"]]
            item = ItemEstoque(
                sku=item_data["sku"],
                nome=item_data["nome"],
                descricao=f"Item de {item_data['categoria']}",
                categoria_id=categoria.id,
                unidade=item_data["unidade"],
                estoque_atual=item_data["estoque"],
                estoque_minimo=item_data["min"],
                estoque_maximo=item_data["max"],
                custo_unitario=item_data["custo"],
                preco_venda=item_data["venda"],
                percentual_markup=((item_data["venda"] - item_data["custo"]) / item_data["custo"]) * 100,
                fornecedor=random.choice(["Distribuidora SP", "Fornecedor Nacional", "Importadora Ltda"]),
                localizacao_estoque=f"Prateleira {random.choice(['A', 'B', 'C'])}-{random.randint(1, 10)}",
                ativo=True
            )
            session.add(item)
            await session.flush()
            itens_criados.append(item)
            print(f"  ✓ Criado: {item_data['nome']}")
        else:
            itens_criados.append(existing)
            print(f"  - Já existe: {item_data['nome']}")
    
    await session.commit()
    return itens_criados


async def seed_ordens_servico(
    session: AsyncSessionLocal,
    clientes: list,
    tecnicos: dict,
    categorias_servico: dict,
    itens_estoque: list,
    admin_id: str
):
    """Cria 50 ordens de serviço (idempotente)."""
    print("Criando ordens de serviço...")
    
    # Distribuição de status
    status_distribuicao = (
        [StatusOS.PENDENTE] * 8 +
        [StatusOS.CONFIRMADA] * 5 +
        [StatusOS.EM_ANDAMENTO] * 6 +
        [StatusOS.CONCLUIDA] * 25 +
        [StatusOS.CANCELADA] * 4 +
        [StatusOS.AGUARDANDO] * 2
    )
    
    # Distribuição de prioridade
    prioridade_distribuicao = (
        [PrioridadeOS.NORMAL] * 20 +
        [PrioridadeOS.ALTA] * 15 +
        [PrioridadeOS.BAIXA] * 10 +
        [PrioridadeOS.URGENTE] * 5
    )
    
    random.shuffle(status_distribuicao)
    random.shuffle(prioridade_distribuicao)
    
    ordens_criadas = []
    for i in range(50):
        numero_os = f"OS-2025-{i+1:05d}"
        result = await session.execute(
            select(OrdemServico).where(OrdemServico.numero_os == numero_os)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            cliente = random.choice(clientes)
            tecnico = random.choice(list(tecnicos.values()))
            categoria = random.choice(list(categorias_servico.values()))
            status = status_distribuicao[i]
            prioridade = prioridade_distribuicao[i]
            
            valor_estimado = random.uniform(150.0, 2500.0)
            
            # Data de criação nos últimos 6 meses
            dias_atras = random.randint(0, 180)
            data_criacao = datetime.now(UTC) - timedelta(days=dias_atras)
            
            # Data de conclusão se status for concluída
            data_conclusao = None
            valor_final = 0.0
            if status == StatusOS.CONCLUIDA:
                dias_conclusao = random.randint(1, 30)
                data_conclusao = data_criacao + timedelta(days=dias_conclusao)
                valor_final = valor_estimado * random.uniform(0.8, 1.2)
            
            # Status de pagamento
            status_pagamento = StatusPagamento.PENDENTE
            if status == StatusOS.CONCLUIDA:
                if (datetime.now(UTC) - data_conclusao).days > 7:
                    status_pagamento = StatusPagamento.PAGO
                else:
                    status_pagamento = random.choice([StatusPagamento.PAGO, StatusPagamento.PENDENTE])
            
            os_data = {
                "numero_os": numero_os,
                "cliente_id": cliente.id,
                "tecnico_id": tecnico.id,
                "status": status,
                "prioridade": prioridade,
                "tipo_servico_id": categoria.id,
                "titulo": f"Serviço de {categoria.nome}",
                "descricao": f"Realização de serviço de {categoria.nome} para cliente {cliente.nome}. Inclui verificação técnica e reparos necessários.",
                "valor_estimado": valor_estimado,
                "valor_final": valor_final,
                "status_pagamento": status_pagamento,
                "data_conclusao": data_conclusao,
                "criado_por": admin_id,
                "criado_em": data_criacao
            }
            
            ordem = OrdemServico(**os_data)
            session.add(ordem)
            await session.flush()
            
            # Adicionar itens e checklist se concluída
            if status == StatusOS.CONCLUIDA:
                # 2-4 itens de checklist
                for j in range(random.randint(2, 4)):
                    checklist = ChecklistOrdemServico(
                        ordem_servico_id=ordem.id,
                        descricao=f"Verificação {j+1} - {categoria.nome}",
                        concluido=True,
                        concluido_em=data_conclusao,
                        concluido_por=tecnico.id
                    )
                    session.add(checklist)
                
                # 1-3 itens/materiais utilizados
                for k in range(random.randint(1, 3)):
                    item_estoque = random.choice(itens_estoque)
                    qtd_item = random.randint(1, 5)
                    item_os = ItemOrdemServico(
                        ordem_servico_id=ordem.id,
                        item_estoque_id=item_estoque.id,
                        descricao=item_estoque.nome,
                        quantidade=qtd_item,
                        unidade=item_estoque.unidade.value,
                        custo_unitario=item_estoque.custo_unitario,
                        custo_total=item_estoque.custo_unitario * qtd_item
                    )
                    session.add(item_os)
            
            ordens_criadas.append(ordem)
            print(f"  ✓ Criado: {numero_os}")
        else:
            ordens_criadas.append(existing)
            print(f"  - Já existe: {numero_os}")
    
    await session.commit()
    return ordens_criadas


async def seed_orcamentos(
    session: AsyncSessionLocal,
    clientes: list,
    categorias_servico: dict,
    itens_estoque: list,
    admin_id: str
):
    """Cria 20 orçamentos (idempotente)."""
    print("Criando orçamentos...")
    
    status_distribuicao = (
        [StatusOrcamento.RASCUNHO] * 3 +
        [StatusOrcamento.ENVIADO] * 4 +
        [StatusOrcamento.VISUALIZADO] * 2 +
        [StatusOrcamento.APROVADO] * 6 +
        [StatusOrcamento.RECUSADO] * 3 +
        [StatusOrcamento.EXPIRADO] * 2
    )
    
    random.shuffle(status_distribuicao)
    
    orcamentos_criados = []
    for i in range(20):
        numero_orc = f"ORC-2025-{i+1:05d}"
        result = await session.execute(
            select(Orcamento).where(Orcamento.numero_orcamento == numero_orc)
        )
        existing = result.scalar_one_or_none()
        
        if not existing:
            cliente = random.choice(clientes)
            categoria = random.choice(list(categorias_servico.values()))
            status = status_distribuicao[i]
            
            dias_atras = random.randint(0, 90)
            data_criacao = datetime.now(UTC) - timedelta(days=dias_atras)
            validade_dias = random.randint(15, 30)
            
            # 2-5 itens
            num_itens = random.randint(2, 5)
            subtotal = 0.0
            itens_orc = []
            
            for j in range(num_itens):
                item_estoque = random.choice(itens_estoque)
                quantidade = random.randint(1, 5)
                preco_unitario = item_estoque.preco_venda
                preco_total = quantidade * preco_unitario
                subtotal += preco_total
                
                itens_orc.append({
                    "descricao": item_estoque.nome,
                    "quantidade": quantidade,
                    "unidade": item_estoque.unidade.value,
                    "preco_unitario": preco_unitario,
                    "preco_total": preco_total,
                    "ordem": j
                })
            
            desconto_percentual = random.uniform(0, 15) if random.random() > 0.5 else 0
            valor_desconto = subtotal * (desconto_percentual / 100)
            total = subtotal - valor_desconto
            
            orcamento = Orcamento(
                numero_orcamento=numero_orc,
                cliente_id=cliente.id,
                criado_por=admin_id,
                status=status,
                titulo=f"Orçamento para {categoria.nome}",
                descricao=f"Orçamento para serviços de {categoria.nome} incluindo materiais e mão de obra.",
                valido_ate=data_criacao + timedelta(days=validade_dias),
                subtotal=subtotal,
                tipo_desconto="percentual" if desconto_percentual > 0 else None,
                valor_desconto=valor_desconto,
                total=total,
                criado_em=data_criacao
            )
            
            if status == StatusOrcamento.APROVADO:
                orcamento.aprovado_em = data_criacao + timedelta(days=random.randint(1, 10))
            elif status == StatusOrcamento.ENVIADO:
                orcamento.enviado_em = data_criacao + timedelta(days=random.randint(1, 3))
            elif status == StatusOrcamento.VISUALIZADO:
                orcamento.enviado_em = data_criacao + timedelta(days=1)
                orcamento.visualizado_em = data_criacao + timedelta(days=random.randint(2, 5))
            
            session.add(orcamento)
            await session.flush()
            
            # Adicionar itens
            for item_data in itens_orc:
                item = ItemOrcamento(
                    orcamento_id=orcamento.id,
                    descricao=item_data["descricao"],
                    quantidade=item_data["quantidade"],
                    unidade=item_data["unidade"],
                    preco_unitario=item_data["preco_unitario"],
                    preco_total=item_data["preco_total"],
                    ordem=item_data["ordem"]
                )
                session.add(item)
            
            orcamentos_criados.append(orcamento)
            print(f"  ✓ Criado: {numero_orc}")
        else:
            orcamentos_criados.append(existing)
            print(f"  - Já existe: {numero_orc}")
    
    await session.commit()
    return orcamentos_criados


async def seed_transacoes(
    session: AsyncSessionLocal,
    ordens_servico: list,
    categorias_financeiras: dict,
    admin_id: str
):
    """Cria transações financeiras para os últimos 3 meses (idempotente)."""
    print("Criando transações financeiras...")
    
    transacoes_criadas = []
    contador = 0
    
    # Receitas de OS concluídas
    for os in ordens_servico:
        if os.status == StatusOS.CONCLUIDA and os.valor_final > 0:
            numero_trans = f"TRX-2025-{contador+1:05d}"
            result = await session.execute(
                select(Transacao).where(Transacao.numero_transacao == numero_trans)
            )
            existing = result.scalar_one_or_none()
            
            if not existing:
                # Garantir que algumas transações tenham datas nos últimos 7 dias
                if random.random() < 0.3:  # 30% das transações nos últimos 7 dias
                    dias_pagamento = random.randint(0, 7)
                else:
                    dias_pagamento = random.randint(0, 30)
                data_pagamento = os.data_conclusao + timedelta(days=dias_pagamento)
                status = StatusTransacao.PAGO if (datetime.now(UTC) - data_pagamento).days >= 0 else StatusTransacao.PENDENTE
                
                transacao = Transacao(
                    numero_transacao=numero_trans,
                    tipo=TipoTransacao.RECEITA,
                    categoria_id=categorias_financeiras["Serviços Prestados"].id,
                    ordem_servico_id=os.id,
                    cliente_id=os.cliente_id,
                    descricao=f"Pagamento OS {os.numero_os}",
                    valor=os.valor_final,
                    data_vencimento=os.data_conclusao + timedelta(days=7),
                    data_pagamento=data_pagamento if status == StatusTransacao.PAGO else None,
                    status=status,
                    forma_pagamento=random.choice(["pix", "cartao_credito", "transferencia"]),
                    criado_por=admin_id
                )
                session.add(transacao)
                await session.flush()
                transacoes_criadas.append(transacao)
                contador += 1
                print(f"  ✓ Criado: {numero_trans}")
            else:
                transacoes_criadas.append(existing)
    
    # Despesas de operação (últimos 3 meses, com foco nos últimos 7 dias)
    despesas_tipos = [
        {"categoria": "Materiais", "valor_min": 50, "valor_max": 500, "frequencia": 3},  # 2-3 por semana
        {"categoria": "Aluguel", "valor_min": 2800, "valor_max": 2800, "frequencia": 1},  # 1 por mês
        {"categoria": "Combustível", "valor_min": 80, "valor_max": 200, "frequencia": 6},  # 4-8 por mês
        {"categoria": "Equipamentos", "valor_min": 150, "valor_max": 800, "frequencia": 2},  # 1-2 por mês
        {"categoria": "Alimentação", "valor_min": 30, "valor_max": 120, "frequencia": 12}  # 8-15 por mês
    ]
    
    for despesa_tipo in despesas_tipos:
        categoria = categorias_financeiras[despesa_tipo["categoria"]]
        semanas = 12  # 3 meses
        
        for semana in range(semanas):
            num_transacoes = random.randint(1, despesa_tipo["frequencia"] // 4 + 1)
            
            for _ in range(num_transacoes):
                numero_trans = f"TRX-2025-{contador+1:05d}"
                result = await session.execute(
                    select(Transacao).where(Transacao.numero_transacao == numero_trans)
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    # Garantir que algumas despesas tenham datas nos últimos 7 dias
                    if random.random() < 0.4:  # 40% das despesas nos últimos 7 dias
                        dias_atras = random.randint(0, 7)
                    else:
                        dias_atras = random.randint(0, 90)
                    data_vencimento = datetime.now(UTC) - timedelta(days=dias_atras)
                    valor = random.uniform(despesa_tipo["valor_min"], despesa_tipo["valor_max"])
                    
                    transacao = Transacao(
                        numero_transacao=numero_trans,
                        tipo=TipoTransacao.DESPESA,
                        categoria_id=categoria.id,
                        descricao=f"{despesa_tipo['categoria']} - Semana {semana + 1}",
                        valor=valor,
                        data_vencimento=data_vencimento,
                        data_pagamento=data_vencimento if random.random() > 0.2 else None,
                        status=random.choice([StatusTransacao.PAGO, StatusTransacao.PAGO, StatusTransacao.PENDENTE]),
                        criado_por=admin_id
                    )
                    session.add(transacao)
                    await session.flush()
                    transacoes_criadas.append(transacao)
                    contador += 1
                    print(f"  ✓ Criado: {numero_trans}")
                else:
                    transacoes_criadas.append(existing)
    
    await session.commit()
    return transacoes_criadas


async def seed_agenda(
    session: AsyncSessionLocal,
    ordens_servico: list,
    tecnicos: dict,
    clientes: list
):
    """Cria eventos de agenda para as próximas 2 semanas (idempotente)."""
    print("Criando eventos de agenda...")
    
    eventos_criados = []
    contador = 0
    
    # Cores para técnicos
    cores_tecnicos = {
        "joao@assistenciaimpacto.com.br": "#6C63FF",
        "maria@assistenciaimpacto.com.br": "#00D4FF",
        "carlos@assistenciaimpacto.com.br": "#10B981"
    }
    
    # Para cada técnico, criar eventos
    for email_tecnico, tecnico in tecnicos.items():
        cor = cores_tecnicos.get(email_tecnico, "#6C63FF")
        
        # 2-3 serviços por dia útil nas próximas 2 semanas
        data_atual = datetime.now(BRT)
        dias = 14
        
        for dia in range(dias):
            data_evento = data_atual + timedelta(days=dia)
            
            # Pular finais de semana
            if data_evento.weekday() >= 5:
                continue
            
            # Reunião de equipe semanal (segunda-feira 08:00)
            if data_evento.weekday() == 0:
                numero_evento = f"EVT-{contador+1:05d}"
                result = await session.execute(
                    select(Agenda).where(Agenda.id == numero_evento)
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    evento = Agenda(
                        id=numero_evento,
                        titulo="Reunião de Equipe",
                        tecnico_id=tecnico.id,
                        data_hora_inicio=data_evento.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=BRT),
                        data_hora_fim=data_evento.replace(hour=9, minute=0, second=0, microsecond=0, tzinfo=BRT),
                        tipo_evento=TipoEvento.REUNIAO,
                        status=StatusEvento.AGENDADO,
                        cor=cor,
                        observacoes="Reunião semanal de alinhamento da equipe"
                    )
                    session.add(evento)
                    await session.flush()
                    eventos_criados.append(evento)
                    contador += 1
                    print(f"  ✓ Criado: Reunião - {email_tecnico}")
                else:
                    eventos_criados.append(existing)
            
            # 2-3 serviços por dia
            num_servicos = random.randint(2, 3)
            hora_base = 8  # 08:00 (horário comercial)
            
            for i in range(num_servicos):
                numero_evento = f"EVT-{contador+1:05d}"
                result = await session.execute(
                    select(Agenda).where(Agenda.id == numero_evento)
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    hora_inicio = hora_base + (i * 3)
                    duracao = random.choice([1, 2, 3])  # 1-3 horas
                    
                    # Tentar vincular a uma OS
                    os_pendente = random.choice([os for os in ordens_servico if os.status in [StatusOS.PENDENTE, StatusOS.CONFIRMADA]])
                    
                    evento = Agenda(
                        id=numero_evento,
                        titulo=f"Serviço - {os_pendente.titulo}",
                        ordem_servico_id=os_pendente.id,
                        tecnico_id=tecnico.id,
                        cliente_id=os_pendente.cliente_id,
                        data_hora_inicio=data_evento.replace(hour=hora_inicio, minute=0, second=0, microsecond=0, tzinfo=BRT),
                        data_hora_fim=data_evento.replace(hour=hora_inicio + duracao, minute=0, second=0, microsecond=0, tzinfo=BRT),
                        tipo_evento=TipoEvento.SERVICO,
                        status=StatusEvento.AGENDADO,
                        cor=cor,
                        observacoes=f"Execução de OS {os_pendente.numero_os}"
                    )
                    session.add(evento)
                    await session.flush()
                    eventos_criados.append(evento)
                    contador += 1
                    print(f"  ✓ Criado: Serviço - {email_tecnico}")
                else:
                    eventos_criados.append(existing)
    
    await session.commit()
    return eventos_criados


async def main():
    """Função principal de seed."""
    print("=" * 60)
    print("INICIANDO SEED DO BANCO DE DADOS")
    print("=" * 60)
    
    async with AsyncSessionLocal() as session:
        try:
            # FASE 1: Usuários
            usuarios = await seed_usuarios(session)
            admin_id = usuarios["admin@assistenciaimpacto.com.br"].id
            tecnicos = {k: v for k, v in usuarios.items() if k != "admin@assistenciaimpacto.com.br"}
            
            # FASE 2: Categorias
            categorias_servico = await seed_categorias_servico(session)
            categorias_estoque = await seed_categorias_estoque(session)
            categorias_financeiras = await seed_categorias_financeiras(session)
            
            # FASE 2.5: Configurações
            configuracoes = await seed_configuracoes(session, admin_id)
            
            # FASE 3: Clientes
            clientes = await seed_clientes(session, admin_id)
            
            # FASE 4: Estoque
            itens_estoque = await seed_itens_estoque(session, categorias_estoque)
            
            # FASE 5: Ordens de Serviço
            ordens_servico = await seed_ordens_servico(
                session, clientes, tecnicos, categorias_servico, itens_estoque, admin_id
            )
            
            # FASE 6: Orçamentos
            orcamentos = await seed_orcamentos(
                session, clientes, categorias_servico, itens_estoque, admin_id
            )
            
            # FASE 7: Transações Financeiras
            transacoes = await seed_transacoes(
                session, ordens_servico, categorias_financeiras, admin_id
            )
            
            # FASE 8: Agenda
            eventos_agenda = await seed_agenda(
                session, ordens_servico, tecnicos, clientes
            )
            
            print("=" * 60)
            print("SEED CONCLUÍDO COM SUCESSO!")
            print("=" * 60)
            print(f"Usuários: {len(usuarios)}")
            print(f"Categorias de Serviço: {len(categorias_servico)}")
            print(f"Clientes: {len(clientes)}")
            print(f"Itens de Estoque: {len(itens_estoque)}")
            print(f"Ordens de Serviço: {len(ordens_servico)}")
            print(f"Orçamentos: {len(orcamentos)}")
            print(f"Transações: {len(transacoes)}")
            print(f"Eventos de Agenda: {len(eventos_agenda)}")
            print("=" * 60)
            
        except Exception as e:
            print(f"ERRO durante o seed: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
