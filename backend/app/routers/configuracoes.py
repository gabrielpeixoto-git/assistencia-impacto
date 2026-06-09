from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.configuracao import ConfiguracaoResponse, ConfiguracaoUpdate
from app.config import settings
from app.dependencies import get_usuario_atual, require_admin, get_db, get_redis
from app.models.usuario import Usuario
from app.models.configuracao import Configuracao
from app.models.cliente import Cliente
from app.models.ordem_servico import OrdemServico
from app.models.financeiro import Transacao
from loguru import logger
from redis.asyncio import Redis
import json

router = APIRouter(prefix="/api/configuracoes", tags=["configuracoes"])


@router.get("", response_model=ConfiguracaoResponse)
async def obter_configuracoes(
    current_user: Usuario = Depends(get_usuario_atual),
    db: AsyncSession = Depends(get_db)
):
    """Retorna as configurações atuais do sistema (apenas configs não sensíveis).
    
    Busca primeiro no banco de dados. Se não encontrar, usa fallback do .env.
    """
    # Mapeamento de chaves do banco para campos do response
    config_keys = {
        'nome_empresa': settings.nome_empresa,
        'cnpj_empresa': settings.cnpj_empresa,
        'telefone_empresa': settings.telefone_empresa,
        'email_empresa': settings.email_empresa,
        'endereco_empresa': settings.endereco_empresa,
        'smtp_host': settings.smtp_host,
        'smtp_porta': str(settings.smtp_porta),
        'smtp_usuario': settings.smtp_usuario,
        'email_remetente': settings.email_remetente,
        'nome_remetente': settings.nome_remetente,
        'evolution_api_url': settings.evolution_api_url,
        'whatsapp_telefone': settings.whatsapp_telefone,
        'viacep_api_url': settings.viacep_api_url,
        'url_frontend': settings.url_frontend,
        'ambiente': settings.ambiente,
        'permitir_registro_publico': str(settings.permitir_registro_publico),
        'tamanho_maximo_upload_mb': str(settings.tamanho_maximo_upload_mb),
        'tipos_imagem_permitidos': settings.tipos_imagem_permitidos
    }
    
    # Buscar configurações no banco
    result = await db.execute(select(Configuracao))
    db_configs = result.scalars().all()
    
    # Criar dicionário com valores do banco ou fallback
    config_dict = {}
    for config in db_configs:
        config_dict[config.chave] = config.valor
    
    # Helper para obter valor com fallback
    def get_config(key: str, fallback: str) -> str:
        return config_dict.get(key, fallback)
    
    def get_config_bool(key: str, fallback: bool) -> bool:
        valor = config_dict.get(key, str(fallback))
        return valor.lower() == 'true'
    
    return ConfiguracaoResponse(
        # Dados da Empresa
        nome_empresa=get_config('nome_empresa', settings.nome_empresa),
        cnpj_empresa=get_config('cnpj_empresa', settings.cnpj_empresa),
        telefone_empresa=get_config('telefone_empresa', settings.telefone_empresa),
        email_empresa=get_config('email_empresa', settings.email_empresa),
        endereco_empresa=get_config('endereco_empresa', settings.endereco_empresa),
        
        # Configurações de Email (sem senha)
        smtp_host=get_config('smtp_host', settings.smtp_host),
        smtp_porta=int(get_config('smtp_porta', str(settings.smtp_porta))),
        smtp_usuario=get_config('smtp_usuario', settings.smtp_usuario),
        email_remetente=get_config('email_remetente', settings.email_remetente),
        nome_remetente=get_config('nome_remetente', settings.nome_remetente),
        
        # Configurações de WhatsApp (sem API key)
        evolution_api_url=get_config('evolution_api_url', settings.evolution_api_url),
        whatsapp_telefone=get_config('whatsapp_telefone', settings.whatsapp_telefone),
        
        # APIs Externas (sem chaves sensíveis)
        viacep_api_url=get_config('viacep_api_url', settings.viacep_api_url),
        
        # Frontend
        url_frontend=get_config('url_frontend', settings.url_frontend),
        
        # Ambiente
        ambiente=get_config('ambiente', settings.ambiente),
        permitir_registro_publico=get_config_bool('permitir_registro_publico', settings.permitir_registro_publico),
        
        # Uploads
        tamanho_maximo_upload_mb=int(get_config('tamanho_maximo_upload_mb', str(settings.tamanho_maximo_upload_mb))),
        tipos_imagem_permitidos=get_config('tipos_imagem_permitidos', settings.tipos_imagem_permitidos),
        
        # Preferências de Notificação
        notif_nova_os=get_config_bool('notif_nova_os', True),
        notif_orcamento_aprovado=get_config_bool('notif_orcamento_aprovado', True),
        notif_orcamento_rejeitado=get_config_bool('notif_orcamento_rejeitado', True),
        notif_agendamento_proximo=get_config_bool('notif_agendamento_proximo', True),
        notif_estoque_baixo=get_config_bool('notif_estoque_baixo', True),
        notif_relatorio_semanal=get_config_bool('notif_relatorio_semanal', False),
        notif_canal_email=get_config_bool('notif_canal_email', True),
        notif_canal_sistema=get_config_bool('notif_canal_sistema', True),
        notif_frequencia=get_config('notif_frequencia', 'imediato'),
        
        # Preferências de Aparência
        tema_dark_mode=get_config_bool('tema_dark_mode', False),
        tema_cor_primaria=get_config('tema_cor_primaria', 'roxo'),
        tema_densidade=get_config('tema_densidade', 'normal'),
        
        # Configurações Regionais
        regiao_moeda=get_config('regiao_moeda', 'BRL'),
        regiao_fuso_horario=get_config('regiao_fuso_horario', 'America/Sao_Paulo'),
        regiao_formato_data=get_config('regiao_formato_data', 'DD/MM/AAAA'),
        regiao_idioma=get_config('regiao_idioma', 'pt-BR')
    )


@router.put("", response_model=ConfiguracaoResponse)
async def atualizar_configuracoes(
    configuracao_data: ConfiguracaoUpdate,
    usuario_atual: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza configurações do sistema (apenas configs não sensíveis).
    Requer permissão de administrador.
    
    Salva as configurações no banco de dados usando o model Configuracao (chave/valor).
    """
    logger.info(f"Atualizando configurações por admin {usuario_atual.email}")
    
    # Mapeamento de campos para chaves do banco
    campos_para_atualizar = []
    
    if configuracao_data.nome_empresa is not None:
        campos_para_atualizar.append(('nome_empresa', configuracao_data.nome_empresa))
    if configuracao_data.cnpj_empresa is not None:
        campos_para_atualizar.append(('cnpj_empresa', configuracao_data.cnpj_empresa))
    if configuracao_data.telefone_empresa is not None:
        campos_para_atualizar.append(('telefone_empresa', configuracao_data.telefone_empresa))
    if configuracao_data.email_empresa is not None:
        campos_para_atualizar.append(('email_empresa', configuracao_data.email_empresa))
    if configuracao_data.endereco_empresa is not None:
        campos_para_atualizar.append(('endereco_empresa', configuracao_data.endereco_empresa))
    if configuracao_data.smtp_host is not None:
        campos_para_atualizar.append(('smtp_host', configuracao_data.smtp_host))
    if configuracao_data.smtp_porta is not None:
        campos_para_atualizar.append(('smtp_porta', str(configuracao_data.smtp_porta)))
    if configuracao_data.smtp_usuario is not None:
        campos_para_atualizar.append(('smtp_usuario', configuracao_data.smtp_usuario))
    if configuracao_data.email_remetente is not None:
        campos_para_atualizar.append(('email_remetente', configuracao_data.email_remetente))
    if configuracao_data.nome_remetente is not None:
        campos_para_atualizar.append(('nome_remetente', configuracao_data.nome_remetente))
    if configuracao_data.evolution_api_url is not None:
        campos_para_atualizar.append(('evolution_api_url', configuracao_data.evolution_api_url))
    if configuracao_data.whatsapp_telefone is not None:
        campos_para_atualizar.append(('whatsapp_telefone', configuracao_data.whatsapp_telefone))
    if configuracao_data.url_frontend is not None:
        campos_para_atualizar.append(('url_frontend', configuracao_data.url_frontend))
    if configuracao_data.ambiente is not None:
        campos_para_atualizar.append(('ambiente', configuracao_data.ambiente))
    if configuracao_data.permitir_registro_publico is not None:
        campos_para_atualizar.append(('permitir_registro_publico', str(configuracao_data.permitir_registro_publico)))
    if configuracao_data.tamanho_maximo_upload_mb is not None:
        campos_para_atualizar.append(('tamanho_maximo_upload_mb', str(configuracao_data.tamanho_maximo_upload_mb)))
    if configuracao_data.tipos_imagem_permitidos is not None:
        campos_para_atualizar.append(('tipos_imagem_permitidos', configuracao_data.tipos_imagem_permitidos))
    
    # Preferências de Notificação
    if configuracao_data.notif_nova_os is not None:
        campos_para_atualizar.append(('notif_nova_os', str(configuracao_data.notif_nova_os)))
    if configuracao_data.notif_orcamento_aprovado is not None:
        campos_para_atualizar.append(('notif_orcamento_aprovado', str(configuracao_data.notif_orcamento_aprovado)))
    if configuracao_data.notif_orcamento_rejeitado is not None:
        campos_para_atualizar.append(('notif_orcamento_rejeitado', str(configuracao_data.notif_orcamento_rejeitado)))
    if configuracao_data.notif_agendamento_proximo is not None:
        campos_para_atualizar.append(('notif_agendamento_proximo', str(configuracao_data.notif_agendamento_proximo)))
    if configuracao_data.notif_estoque_baixo is not None:
        campos_para_atualizar.append(('notif_estoque_baixo', str(configuracao_data.notif_estoque_baixo)))
    if configuracao_data.notif_relatorio_semanal is not None:
        campos_para_atualizar.append(('notif_relatorio_semanal', str(configuracao_data.notif_relatorio_semanal)))
    if configuracao_data.notif_canal_email is not None:
        campos_para_atualizar.append(('notif_canal_email', str(configuracao_data.notif_canal_email)))
    if configuracao_data.notif_canal_sistema is not None:
        campos_para_atualizar.append(('notif_canal_sistema', str(configuracao_data.notif_canal_sistema)))
    if configuracao_data.notif_frequencia is not None:
        campos_para_atualizar.append(('notif_frequencia', configuracao_data.notif_frequencia))
    
    # Preferências de Aparência
    if configuracao_data.tema_dark_mode is not None:
        campos_para_atualizar.append(('tema_dark_mode', str(configuracao_data.tema_dark_mode)))
    if configuracao_data.tema_cor_primaria is not None:
        campos_para_atualizar.append(('tema_cor_primaria', configuracao_data.tema_cor_primaria))
    if configuracao_data.tema_densidade is not None:
        campos_para_atualizar.append(('tema_densidade', configuracao_data.tema_densidade))
    
    # Configurações Regionais
    if configuracao_data.regiao_moeda is not None:
        campos_para_atualizar.append(('regiao_moeda', configuracao_data.regiao_moeda))
    if configuracao_data.regiao_fuso_horario is not None:
        campos_para_atualizar.append(('regiao_fuso_horario', configuracao_data.regiao_fuso_horario))
    if configuracao_data.regiao_formato_data is not None:
        campos_para_atualizar.append(('regiao_formato_data', configuracao_data.regiao_formato_data))
    if configuracao_data.regiao_idioma is not None:
        campos_para_atualizar.append(('regiao_idioma', configuracao_data.regiao_idioma))
    
    # Atualizar ou inserir cada configuração no banco
    for chave, valor in campos_para_atualizar:
        result = await db.execute(select(Configuracao).where(Configuracao.chave == chave))
        config_existente = result.scalar_one_or_none()
        
        if config_existente:
            config_existente.valor = valor
            config_existente.atualizado_por = usuario_atual.id
        else:
            nova_config = Configuracao(
                chave=chave,
                valor=valor,
                atualizado_por=usuario_atual.id
            )
            db.add(nova_config)
    
    await db.commit()
    logger.info(f"Configurações atualizadas com sucesso: {len(campos_para_atualizar)} campos")
    
    # Retornar as configurações atualizadas
    return await obter_configuracoes(usuario_atual, db)


@router.get("/exportar-dados")
async def exportar_dados(
    usuario_atual: Usuario = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Exporta dados do sistema (clientes, OS, transações) em JSON."""
    logger.info(f"Exportando dados por admin {usuario_atual.email}")

    # Buscar clientes
    result_clientes = await db.execute(select(Cliente))
    clientes = result_clientes.scalars().all()

    # Buscar ordens de serviço
    result_os = await db.execute(select(OrdemServico))
    ordens_servico = result_os.scalars().all()

    # Buscar transações
    result_transacoes = await db.execute(select(Transacao))
    transacoes = result_transacoes.scalars().all()

    # Serializar dados
    dados_export = {
        "clientes": [
            {
                "id": c.id,
                "nome": c.nome,
                "email": c.email,
                "telefone": c.telefone,
                "tipo_cliente": c.tipo_cliente.value if c.tipo_cliente else None,
                "ativo": c.ativo,
                "criado_em": c.criado_em.isoformat() if c.criado_em else None
            }
            for c in clientes
        ],
        "ordens_servico": [
            {
                "id": os.id,
                "numero_os": os.numero_os,
                "titulo": os.titulo,
                "status": os.status.value if os.status else None,
                "cliente_id": os.cliente_id,
                "valor_final": float(os.valor_final) if os.valor_final else None,
                "criado_em": os.criado_em.isoformat() if os.criado_em else None
            }
            for os in ordens_servico
        ],
        "transacoes": [
            {
                "id": t.id,
                "numero_transacao": t.numero_transacao,
                "tipo": t.tipo.value if t.tipo else None,
                "valor": float(t.valor),
                "status": t.status.value if t.status else None,
                "data_vencimento": t.data_vencimento.isoformat() if t.data_vencimento else None,
                "criado_em": t.criado_em.isoformat() if t.criado_em else None
            }
            for t in transacoes
        ],
        "exportado_em": logger.info("Dados exportados com sucesso")
    }

    # Gerar JSON string
    json_str = json.dumps(dados_export, indent=2, ensure_ascii=False)

    # Retornar como arquivo para download
    from datetime import datetime
    filename = f"export_dados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return StreamingResponse(
        iter([json_str]),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.delete("/limpar-cache")
async def limpar_cache(
    usuario_atual: Usuario = Depends(require_admin),
    redis: Redis = Depends(get_redis)
):
    """Limpa todo o cache Redis."""
    logger.info(f"Limpando cache Redis por admin {usuario_atual.email}")
    await redis.flushdb()
    return {"mensagem": "Cache limpo com sucesso"}
