from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.notificacao import Notificacao, TipoNotificacao
from app.models.usuario import Usuario
from app.websocket.manager import manager
from datetime import datetime
from typing import Optional, List


class NotificacaoService:
    """Service para lógica de negócio de notificações."""
    
    @staticmethod
    async def criar_notificacao(
        db: AsyncSession,
        usuario_id: str,
        titulo: str,
        mensagem: str,
        tipo: TipoNotificacao,
        link: Optional[str] = None
    ) -> Notificacao:
        """Cria uma nova notificação para um usuário."""
        notificacao = Notificacao(
            usuario_id=usuario_id,
            titulo=titulo,
            mensagem=mensagem,
            tipo=tipo,
            link=link,
            lida=False
        )
        
        db.add(notificacao)
        await db.commit()
        await db.refresh(notificacao)
        
        # Enviar notificação em tempo real via WebSocket se usuário estiver conectado
        if manager.is_user_connected(usuario_id):
            await manager.send_personal_message({
                "type": "notificacao",
                "data": {
                    "id": notificacao.id,
                    "titulo": notificacao.titulo,
                    "mensagem": notificacao.mensagem,
                    "tipo": notificacao.tipo.value,
                    "link": notificacao.link,
                    "lida": notificacao.lida,
                    "criada_em": notificacao.criada_em.isoformat()
                }
            }, usuario_id)
        
        return notificacao
    
    @staticmethod
    async def marcar_como_lida(
        db: AsyncSession,
        notificacao_id: str,
        usuario_id: str
    ) -> Notificacao:
        """Marca uma notificação como lida."""
        query = select(Notificacao).where(
            Notificacao.id == notificacao_id,
            Notificacao.usuario_id == usuario_id
        )
        result = await db.execute(query)
        notificacao = result.scalar_one_or_none()
        
        if not notificacao:
            raise ValueError("Notificação não encontrada")
        
        notificacao.lida = True
        notificacao.lida_em = datetime.utcnow()
        
        await db.commit()
        await db.refresh(notificacao)
        
        return notificacao
    
    @staticmethod
    async def marcar_todas_como_lidas(
        db: AsyncSession,
        usuario_id: str
    ) -> int:
        """Marca todas as notificações de um usuário como lidas."""
        query = select(Notificacao).where(
            Notificacao.usuario_id == usuario_id,
            Notificacao.lida == False
        )
        result = await db.execute(query)
        notificacoes = result.scalars().all()
        
        count = 0
        for notificacao in notificacoes:
            notificacao.lida = True
            notificacao.lida_em = datetime.utcnow()
            count += 1
        
        await db.commit()
        
        return count
    
    @staticmethod
    async def listar_notificacoes_usuario(
        db: AsyncSession,
        usuario_id: str,
        apenas_nao_lidas: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[Notificacao]:
        """Lista notificações de um usuário."""
        query = select(Notificacao).where(Notificacao.usuario_id == usuario_id)
        
        if apenas_nao_lidas:
            query = query.where(Notificacao.lida == False)
        
        query = query.order_by(Notificacao.criada_em.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        notificacoes = result.scalars().all()
        
        return notificacoes
    
    @staticmethod
    async def contar_nao_lidas(
        db: AsyncSession,
        usuario_id: str
    ) -> int:
        """Conta notificações não lidas de um usuário."""
        from sqlalchemy import func
        
        query = select(func.count(Notificacao.id)).where(
            Notificacao.usuario_id == usuario_id,
            Notificacao.lida == False
        )
        result = await db.execute(query)
        count = result.scalar() or 0
        
        return count
    
    @staticmethod
    async def deletar_notificacao(
        db: AsyncSession,
        notificacao_id: str,
        usuario_id: str
    ) -> None:
        """Deleta uma notificação."""
        query = select(Notificacao).where(
            Notificacao.id == notificacao_id,
            Notificacao.usuario_id == usuario_id
        )
        result = await db.execute(query)
        notificacao = result.scalar_one_or_none()
        
        if not notificacao:
            raise ValueError("Notificação não encontrada")
        
        await db.delete(notificacao)
        await db.commit()
    
    @staticmethod
    async def notificar_ordem_servico_criada(
        db: AsyncSession,
        ordem_servico_id: str,
        tecnico_id: str,
        cliente_nome: str
    ) -> Notificacao:
        """Envia notificação quando uma ordem de serviço é criada."""
        return await NotificacaoService.criar_notificacao(
            db=db,
            usuario_id=tecnico_id,
            titulo="Nova Ordem de Serviço",
            mensagem=f"Nova ordem de serviço criada para o cliente {cliente_nome}",
            tipo=TipoNotificacao.INFO,
            link=f"/ordens-servico/{ordem_servico_id}"
        )
    
    @staticmethod
    async def notificar_orcamento_aprovado(
        db: AsyncSession,
        orcamento_id: str,
        usuario_id: str,
        cliente_nome: str
    ) -> Notificacao:
        """Envia notificação quando um orçamento é aprovado."""
        return await NotificacaoService.criar_notificacao(
            db=db,
            usuario_id=usuario_id,
            titulo="Orçamento Aprovado",
            mensagem=f"O orçamento para {cliente_nome} foi aprovado pelo cliente",
            tipo=TipoNotificacao.SUCESSO,
            link=f"/orcamentos/{orcamento_id}"
        )
    
    @staticmethod
    async def notificar_estoque_baixo(
        db: AsyncSession,
        item_estoque_id: str,
        item_nome: str,
        usuario_ids: List[str]
    ) -> List[Notificacao]:
        """Envia notificação quando um item de estoque está baixo."""
        notificacoes = []
        for usuario_id in usuario_ids:
            notificacao = await NotificacaoService.criar_notificacao(
                db=db,
                usuario_id=usuario_id,
                titulo="Alerta de Estoque",
                mensagem=f"O item {item_nome} está com estoque abaixo do mínimo",
                tipo=TipoNotificacao.ALERTA,
                link=f"/estoque"
            )
            notificacoes.append(notificacao)
        
        return notificacoes
