"""init

Revision ID: 000_init
Revises: 
Create Date: 2026-06-02 21:38:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '000_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Tabela de usuários
    op.create_table(
        'usuarios',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('nome_completo', sa.String(255), nullable=False),
        sa.Column('senha_hash', sa.String(255), nullable=False),
        sa.Column('perfil', sa.Enum('ADMIN', 'GERENTE', 'TECNICO', 'VISUALIZADOR', name='perfil'), nullable=False),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('verificado', sa.Boolean(), nullable=False),
        sa.Column('ultimo_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Tabela de clientes
    op.create_table(
        'clientes',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('telefone', sa.String(20), nullable=True),
        sa.Column('whatsapp', sa.String(20), nullable=True),
        sa.Column('tipo_documento', sa.Enum('cpf', 'cnpj', name='tipodocumento'), nullable=False),
        sa.Column('numero_documento', sa.String(20), nullable=True),
        sa.Column('tipo_cliente', sa.Enum('residencial', 'comercial', name='tipocliente'), nullable=False),
        sa.Column('logradouro', sa.String(255), nullable=True),
        sa.Column('numero', sa.String(20), nullable=True),
        sa.Column('complemento', sa.String(255), nullable=True),
        sa.Column('bairro', sa.String(100), nullable=True),
        sa.Column('cidade', sa.String(100), nullable=True),
        sa.Column('estado', sa.String(2), nullable=True),
        sa.Column('cep', sa.String(10), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('observacoes', sa.String(2000), nullable=True),
        sa.Column('avaliacao', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_por', sa.String(36), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['criado_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de enderecos de cliente
    op.create_table(
        'enderecos_cliente',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('cliente_id', sa.String(36), nullable=False),
        sa.Column('rotulo', sa.String(50), nullable=False),
        sa.Column('logradouro', sa.String(255), nullable=False),
        sa.Column('numero', sa.String(20), nullable=False),
        sa.Column('complemento', sa.String(255), nullable=True),
        sa.Column('bairro', sa.String(100), nullable=False),
        sa.Column('cidade', sa.String(100), nullable=False),
        sa.Column('estado', sa.String(2), nullable=False),
        sa.Column('cep', sa.String(10), nullable=False),
        sa.Column('padrao', sa.Boolean(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de categorias de serviço
    op.create_table(
        'categorias_servico',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('descricao', sa.String(500), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de categorias financeiras (criar antes de transacoes)
    op.create_table(
        'categorias_financeiras',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('cor', sa.String(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de categorias de estoque (criar antes de itens_estoque)
    op.create_table(
        'categorias_estoque',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('nome', sa.String(100), nullable=False),
        sa.Column('descricao', sa.String(500), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de itens de estoque (criar antes de itens_ordem_servico)
    op.create_table(
        'itens_estoque',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('sku', sa.String(50), nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('descricao', sa.String(1000), nullable=True),
        sa.Column('quantidade', sa.Float(), nullable=False),
        sa.Column('unidade', sa.String(20), nullable=False),
        sa.Column('custo_unitario', sa.Float(), nullable=False),
        sa.Column('categoria_id', sa.String(36), nullable=True),
        sa.Column('minimo', sa.Integer(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias_estoque.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de orçamentos
    op.create_table(
        'orcamentos',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('cliente_id', sa.String(36), nullable=False),
        sa.Column('categoria_servico_id', sa.String(36), nullable=True),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('valor_estimado', sa.Float(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('validade', sa.DateTime(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.ForeignKeyConstraint(['categoria_servico_id'], ['categorias_servico.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de itens de orçamento
    op.create_table(
        'itens_orcamento',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('orcamento_id', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.String(), nullable=False),
        sa.Column('quantidade', sa.Integer(), nullable=False),
        sa.Column('unidade', sa.String(), nullable=False),
        sa.Column('custo_unitario', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de ordens de serviço
    op.create_table(
        'ordens_servico',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('numero_os', sa.String(20), nullable=False),
        sa.Column('cliente_id', sa.String(36), nullable=False),
        sa.Column('categoria_servico_id', sa.String(36), nullable=False),
        sa.Column('tecnico_id', sa.String(36), nullable=True),
        sa.Column('titulo', sa.String(255), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('observacoes_internas', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pendente', 'confirmada', 'em_andamento', 'concluida', 'cancelada', 'aguardando', name='statusos'), nullable=False),
        sa.Column('prioridade', sa.Enum('baixa', 'normal', 'alta', 'urgente', name='prioridadeos'), nullable=False),
        sa.Column('data_agendada', sa.DateTime(timezone=True), nullable=True),
        sa.Column('hora_inicio', sa.String(5), nullable=True),
        sa.Column('hora_fim', sa.String(5), nullable=True),
        sa.Column('data_conclusao', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duracao_minutos', sa.Integer(), nullable=True),
        sa.Column('endereco_id', sa.String(36), nullable=True),
        sa.Column('valor_estimado', sa.Float(), nullable=False),
        sa.Column('valor_final', sa.Float(), nullable=False),
        sa.Column('status_pagamento', sa.Enum('pendente', 'parcial', 'pago', 'atrasado', name='statuspagamento'), nullable=False),
        sa.Column('forma_pagamento', sa.Enum('dinheiro', 'pix', 'cartao_credito', 'transferencia', 'boleto', name='formapagamento'), nullable=True),
        sa.Column('emitir_nota', sa.Boolean(), nullable=False),
        sa.Column('url_assinatura_cliente', sa.String(500), nullable=True),
        sa.Column('criado_por', sa.String(36), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.ForeignKeyConstraint(['categoria_servico_id'], ['categorias_servico.id'], ),
        sa.ForeignKeyConstraint(['tecnico_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['endereco_id'], ['enderecos_cliente.id'], ),
        sa.ForeignKeyConstraint(['criado_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_os')
    )
    
    # Tabela de itens de ordem de serviço
    op.create_table(
        'itens_ordem_servico',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('ordem_servico_id', sa.String(36), nullable=False),
        sa.Column('item_estoque_id', sa.String(36), nullable=True),
        sa.Column('descricao', sa.String(255), nullable=False),
        sa.Column('quantidade', sa.Float(), nullable=False),
        sa.Column('unidade', sa.String(20), nullable=False),
        sa.Column('custo_unitario', sa.Float(), nullable=False),
        sa.Column('custo_total', sa.Float(), nullable=False),
        sa.Column('compra_externa', sa.Boolean(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ordem_servico_id'], ['ordens_servico.id'], ),
        sa.ForeignKeyConstraint(['item_estoque_id'], ['itens_estoque.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de fotos de ordem de serviço
    op.create_table(
        'fotos_ordem_servico',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('ordem_servico_id', sa.String(36), nullable=False),
        sa.Column('enviado_por', sa.String(36), nullable=False),
        sa.Column('url_arquivo', sa.String(500), nullable=False),
        sa.Column('url_miniatura', sa.String(500), nullable=True),
        sa.Column('legenda', sa.String(255), nullable=True),
        sa.Column('tipo_foto', sa.Enum('antes', 'durante', 'depois', 'problema', 'outro', name='tipofoto'), nullable=False),
        sa.Column('tirada_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('criada_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['ordem_servico_id'], ['ordens_servico.id'], ),
        sa.ForeignKeyConstraint(['enviado_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de checklist de ordem de serviço
    op.create_table(
        'checklist_ordem_servico',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('ordem_servico_id', sa.String(36), nullable=False),
        sa.Column('descricao', sa.String(255), nullable=False),
        sa.Column('concluido', sa.Boolean(), nullable=False),
        sa.Column('concluido_em', sa.DateTime(timezone=True), nullable=True),
        sa.Column('concluido_por', sa.String(36), nullable=True),
        sa.ForeignKeyConstraint(['ordem_servico_id'], ['ordens_servico.id'], ),
        sa.ForeignKeyConstraint(['concluido_por'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de agenda
    op.create_table(
        'agenda',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('tecnico_id', sa.String(36), nullable=True),
        sa.Column('cliente_id', sa.String(36), nullable=True),
        sa.Column('data_hora_inicio', sa.DateTime(), nullable=False),
        sa.Column('data_hora_fim', sa.DateTime(), nullable=False),
        sa.Column('tipo_evento', sa.String(), nullable=False),
        sa.Column('cor', sa.String(), nullable=True),
        sa.Column('endereco', sa.String(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tecnico_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de transações financeiras (agora pode referenciar categorias_financeiras)
    op.create_table(
        'transacoes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('valor', sa.Float(), nullable=False),
        sa.Column('categoria_id', sa.Integer(), nullable=True),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('data_transacao', sa.DateTime(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['categoria_id'], ['categorias_financeiras.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de movimentações de estoque
    op.create_table(
        'movimentacoes_estoque',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('item_estoque_id', sa.String(36), nullable=False),
        sa.Column('usuario_id', sa.String(36), nullable=False),
        sa.Column('tipo', sa.String(), nullable=False),
        sa.Column('quantidade', sa.Float(), nullable=False),
        sa.Column('motivo', sa.String(), nullable=True),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['item_estoque_id'], ['itens_estoque.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de notificações
    op.create_table(
        'notificacoes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('usuario_id', sa.String(36), nullable=False),
        sa.Column('titulo', sa.String(), nullable=False),
        sa.Column('corpo', sa.String(), nullable=False),
        sa.Column('lida', sa.Boolean(), nullable=False),
        sa.Column('criada_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de logs de auditoria
    op.create_table(
        'logs_auditoria',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('usuario_id', sa.String(36), nullable=True),
        sa.Column('acao', sa.String(), nullable=False),
        sa.Column('tabela', sa.String(), nullable=False),
        sa.Column('registro_id', sa.Integer(), nullable=False),
        sa.Column('dados_antigos', sa.String(), nullable=True),
        sa.Column('dados_novos', sa.String(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de configurações
    op.create_table(
        'configuracoes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('chave', sa.String(), nullable=False),
        sa.Column('valor', sa.String(), nullable=False),
        sa.Column('descricao', sa.String(), nullable=True),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.Column('atualizado_em', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chave')
    )
    
    # Tabela de sessões
    op.create_table(
        'sessoes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('usuario_id', sa.String(36), nullable=False),
        sa.Column('token', sa.String(), nullable=False),
        sa.Column('expira_em', sa.DateTime(), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Tabela de histórico de acesso
    op.create_table(
        'historico_acesso',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('usuario_id', sa.String(36), nullable=False),
        sa.Column('ip', sa.String(), nullable=False),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('dispositivo', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('historico_acesso')
    op.drop_table('sessoes')
    op.drop_table('configuracoes')
    op.drop_table('logs_auditoria')
    op.drop_table('notificacoes')
    op.drop_table('movimentacoes_estoque')
    op.drop_table('categorias_estoque')
    op.drop_table('itens_estoque')
    op.drop_table('categorias_financeiras')
    op.drop_table('transacoes')
    op.drop_table('agenda')
    op.drop_table('itens_ordem_servico')
    op.drop_table('ordens_servico')
    op.drop_table('itens_orcamento')
    op.drop_table('orcamentos')
    op.drop_table('categorias_servico')
    op.drop_table('clientes')
    op.drop_table('usuarios')
