from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.ordem_servico import OrdemServico, StatusOS, ItemOrdemServico
from app.models.cliente import Cliente
from app.models.usuario import Usuario
from datetime import datetime
from typing import Optional


class OrdemServicoService:
    """Service para lógica de negócio de ordens de serviço."""
    
    @staticmethod
    async def criar_ordem_servico_completa(
        db: AsyncSession,
        cliente_id: str,
        tecnico_id: str,
        tipo_servico_id: str,
        titulo: str,
        descricao: str,
        criado_por: str,
        prioridade: str = "normal",
        data_agendada: Optional[datetime] = None,
        endereco_id: Optional[str] = None,
        valor_estimado: float = 0.0,
        itens: Optional[list] = None
    ) -> OrdemServico:
        """Cria uma ordem de serviço completa com itens."""
        # Gerar número de OS
        numero_os = f"OS{datetime.now().year}{datetime.now().month:02d}"
        
        # Verificar se já existe OS com este número
        query = select(OrdemServico).where(OrdemServico.numero_os == numero_os)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            contador = 1
            while True:
                numero_os = f"OS{datetime.now().year}{datetime.now().month:02d}-{contador}"
                query = select(OrdemServico).where(OrdemServico.numero_os == numero_os)
                result = await db.execute(query)
                if not result.scalar_one_or_none():
                    break
                contador += 1
        
        # Criar ordem de serviço
        os = OrdemServico(
            numero_os=numero_os,
            cliente_id=cliente_id,
            tecnico_id=tecnico_id,
            tipo_servico_id=tipo_servico_id,
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            data_agendada=data_agendada,
            endereco_id=endereco_id,
            valor_estimado=valor_estimado,
            valor_final=valor_estimado,
            status=StatusOS.PENDENTE,
            criado_por=criado_por
        )
        
        db.add(os)
        await db.flush()
        
        # Adicionar itens se fornecidos
        if itens:
            for item_data in itens:
                item = ItemOrdemServico(
                    ordem_servico_id=os.id,
                    item_estoque_id=item_data.get("item_estoque_id"),
                    descricao=item_data["descricao"],
                    quantidade=item_data["quantidade"],
                    unidade=item_data["unidade"],
                    custo_unitario=item_data["custo_unitario"],
                    custo_total=item_data["quantidade"] * item_data["custo_unitario"],
                    compra_externa=item_data.get("compra_externa", False)
                )
                db.add(item)
            
            # Recalcular valor final
            await db.flush()
            query_itens = select(ItemOrdemServico).where(ItemOrdemServico.ordem_servico_id == os.id)
            result_itens = await db.execute(query_itens)
            itens_os = result_itens.scalars().all()
            
            valor_total_itens = sum(i.custo_total for i in itens_os)
            os.valor_final = valor_total_itens
        
        await db.commit()
        await db.refresh(os)
        
        return os
    
    @staticmethod
    async def atualizar_status_ordem_servico(
        db: AsyncSession,
        os_id: str,
        novo_status: StatusOS,
        usuario_id: str
    ) -> OrdemServico:
        """Atualiza o status de uma ordem de serviço com validações."""
        query = select(OrdemServico).where(OrdemServico.id == os_id)
        result = await db.execute(query)
        os = result.scalar_one_or_none()
        
        if not os:
            raise ValueError("Ordem de serviço não encontrada")
        
        # Validações de transição de status
        if novo_status == StatusOS.CONCLUIDA:
            if os.status != StatusOS.EM_ANDAMENTO:
                raise ValueError("Só é possível concluir ordens em andamento")
            os.data_conclusao = datetime.utcnow()
            
            # Calcular duração
            if os.data_agendada:
                duracao = (os.data_conclusao - os.data_agendada).total_seconds() / 60
                os.duracao_minutos = int(duracao)
        
        os.status = novo_status
        await db.commit()
        await db.refresh(os)
        
        return os
    
    @staticmethod
    async def calcular_valor_ordem_servico(
        db: AsyncSession,
        os_id: str
    ) -> float:
        """Calcula o valor total de uma ordem de serviço baseado nos itens."""
        query = select(ItemOrdemServico).where(ItemOrdemServico.ordem_servico_id == os_id)
        result = await db.execute(query)
        itens = result.scalars().all()
        
        valor_total = sum(i.custo_total for i in itens)
        
        # Atualizar ordem de serviço
        query_os = select(OrdemServico).where(OrdemServico.id == os_id)
        result_os = await db.execute(query_os)
        os = result_os.scalar_one_or_none()
        
        if os:
            os.valor_final = valor_total
            await db.commit()
        
        return valor_total
    
    @staticmethod
    async def obter_ordens_servico_por_tecnico(
        db: AsyncSession,
        tecnico_id: str,
        status: Optional[StatusOS] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list[OrdemServico]:
        """Obtém ordens de serviço de um técnico específico."""
        query = select(OrdemServico).where(OrdemServico.tecnico_id == tecnico_id)
        
        if status:
            query = query.where(OrdemServico.status == status)
        
        query = query.order_by(OrdemServico.data_agendada.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        ordens = result.scalars().all()
        
        return ordens
    
    @staticmethod
    async def obter_ordens_servico_por_cliente(
        db: AsyncSession,
        cliente_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> list[OrdemServico]:
        """Obtém ordens de serviço de um cliente específico."""
        query = select(OrdemServico).where(OrdemServico.cliente_id == cliente_id)
        query = query.order_by(OrdemServico.criado_em.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        ordens = result.scalars().all()
        
        return ordens
