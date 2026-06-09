from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.orcamento import Orcamento, ItemOrcamento, StatusOrcamento
from app.models.ordem_servico import OrdemServico, StatusOS, PrioridadeOS
from datetime import datetime, timedelta
from typing import Optional


class OrcamentoService:
    """Service para lógica de negócio de orçamentos."""
    
    @staticmethod
    async def criar_orcamento_completo(
        db: AsyncSession,
        cliente_id: str,
        titulo: str,
        descricao: str,
        criado_por: str,
        valido_ate: Optional[datetime] = None,
        condicoes_pagamento: Optional[str] = None,
        garantia: Optional[str] = None,
        itens: Optional[list] = None
    ) -> Orcamento:
        """Cria um orçamento completo com itens."""
        # Gerar número de orçamento
        numero_orcamento = f"ORC{datetime.now().year}{datetime.now().month:02d}"
        
        # Verificar se já existe orçamento com este número
        query = select(Orcamento).where(Orcamento.numero_orcamento == numero_orcamento)
        result = await db.execute(query)
        if result.scalar_one_or_none():
            contador = 1
            while True:
                numero_orcamento = f"ORC{datetime.now().year}{datetime.now().month:02d}-{contador}"
                query = select(Orcamento).where(Orcamento.numero_orcamento == numero_orcamento)
                result = await db.execute(query)
                if not result.scalar_one_or_none():
                    break
                contador += 1
        
        # Definir validade padrão (30 dias)
        if not valido_ate:
            valido_ate = datetime.now() + timedelta(days=30)
        
        # Criar orçamento
        orcamento = Orcamento(
            numero_orcamento=numero_orcamento,
            cliente_id=cliente_id,
            titulo=titulo,
            descricao=descricao,
            valido_ate=valido_ate,
            condicoes_pagamento=condicoes_pagamento,
            garantia=garantia,
            status=StatusOrcamento.RASCUNHO,
            criado_por=criado_por
        )
        
        db.add(orcamento)
        await db.flush()
        
        # Adicionar itens se fornecidos
        if itens:
            subtotal = 0
            for idx, item_data in enumerate(itens):
                preco_total = item_data["quantidade"] * item_data["preco_unitario"]
                subtotal += preco_total
                
                item = ItemOrcamento(
                    orcamento_id=orcamento.id,
                    item_estoque_id=item_data.get("item_estoque_id"),
                    descricao=item_data["descricao"],
                    quantidade=item_data["quantidade"],
                    unidade=item_data["unidade"],
                    preco_unitario=item_data["preco_unitario"],
                    preco_total=preco_total,
                    ordem=idx
                )
                db.add(item)
            
            orcamento.subtotal = subtotal
            orcamento.total = subtotal
        
        await db.commit()
        await db.refresh(orcamento)
        
        return orcamento
    
    @staticmethod
    async def enviar_orcamento(
        db: AsyncSession,
        orcamento_id: str
    ) -> Orcamento:
        """Envia um orçamento para o cliente."""
        query = select(Orcamento).where(Orcamento.id == orcamento_id)
        result = await db.execute(query)
        orcamento = result.scalar_one_or_none()
        
        if not orcamento:
            raise ValueError("Orçamento não encontrado")
        
        if orcamento.status != StatusOrcamento.RASCUNHO:
            raise ValueError("Só é possível enviar orçamentos em rascunho")
        
        orcamento.status = StatusOrcamento.ENVIADO
        orcamento.enviado_em = datetime.utcnow()
        
        await db.commit()
        await db.refresh(orcamento)
        
        # Notificações são enviadas no router orcamentos.py
        
        return orcamento
    
    @staticmethod
    async def converter_orcamento_os(
        db: AsyncSession,
        orcamento_id: str,
        tecnico_id: str,
        tipo_servico_id: str,
        criado_por: str
    ) -> OrdemServico:
        """Converte um orçamento aprovado em ordem de serviço."""
        query = select(Orcamento).where(Orcamento.id == orcamento_id)
        result = await db.execute(query)
        orcamento = result.scalar_one_or_none()
        
        if not orcamento:
            raise ValueError("Orçamento não encontrado")
        
        if orcamento.status != StatusOrcamento.APROVADO:
            raise ValueError("Só é possível converter orçamentos aprovados")
        
        if orcamento.convertido_para_os_id:
            raise ValueError("Este orçamento já foi convertido em ordem de serviço")
        
        # Gerar número de OS
        numero_os = f"OS{datetime.now().year}{datetime.now().month:02d}"
        
        # Criar ordem de serviço
        os = OrdemServico(
            numero_os=numero_os,
            cliente_id=orcamento.cliente_id,
            tecnico_id=tecnico_id,
            tipo_servico_id=tipo_servico_id,
            titulo=orcamento.titulo,
            descricao=orcamento.descricao,
            observacoes_internas=f"Convertido do orçamento {orcamento.numero_orcamento}",
            prioridade=PrioridadeOS.NORMAL,
            valor_estimado=orcamento.total,
            valor_final=orcamento.total,
            status=StatusOS.PENDENTE,
            criado_por=criado_por
        )
        
        db.add(os)
        await db.flush()
        
        # Copiar itens do orçamento para a OS
        query_itens = select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)
        result_itens = await db.execute(query_itens)
        itens_orcamento = result_itens.scalars().all()
        
        from app.models.ordem_servico import ItemOrdemServico
        for item_orc in itens_orcamento:
            item_os = ItemOrdemServico(
                ordem_servico_id=os.id,
                item_estoque_id=item_orc.item_estoque_id,
                descricao=item_orc.descricao,
                quantidade=item_orc.quantidade,
                unidade=item_orc.unidade,
                custo_unitario=item_orc.preco_unitario,
                custo_total=item_orc.preco_total,
                compra_externa=False
            )
            db.add(item_os)
        
        # Atualizar orçamento
        orcamento.status = StatusOrcamento.CONVERTIDO
        orcamento.convertido_para_os_id = os.id
        
        await db.commit()
        await db.refresh(os)
        
        return os
    
    @staticmethod
    async def verificar_orcamentos_expirados(
        db: AsyncSession
    ) -> int:
        """Verifica e marca orçamentos expirados."""
        agora = datetime.utcnow()
        
        query = select(Orcamento).where(
            and_(
                Orcamento.status == StatusOrcamento.ENVIADO,
                Orcamento.valido_ate < agora
            )
        )
        result = await db.execute(query)
        orcamentos = result.scalars().all()
        
        count = 0
        for orcamento in orcamentos:
            orcamento.status = StatusOrcamento.EXPIRADO
            count += 1
        
        await db.commit()
        
        return count
    
    @staticmethod
    async def calcular_totais_orcamento(
        db: AsyncSession,
        orcamento_id: str,
        tipo_desconto: Optional[str] = None,
        valor_desconto: float = 0,
        taxa_imposto: float = 0
    ) -> dict:
        """Calcula os totais de um orçamento com desconto e imposto."""
        query = select(ItemOrcamento).where(ItemOrcamento.orcamento_id == orcamento_id)
        result = await db.execute(query)
        itens = result.scalars().all()
        
        subtotal = sum(i.preco_total for i in itens)
        
        # Calcular desconto
        if tipo_desconto == "percentual":
            desconto = subtotal * (valor_desconto / 100)
        else:
            desconto = valor_desconto
        
        # Calcular imposto
        imposto = (subtotal - desconto) * (taxa_imposto / 100)
        
        total = subtotal - desconto + imposto
        
        # Atualizar orçamento
        query_orc = select(Orcamento).where(Orcamento.id == orcamento_id)
        result_orc = await db.execute(query_orc)
        orcamento = result_orc.scalar_one_or_none()
        
        if orcamento:
            orcamento.subtotal = subtotal
            orcamento.tipo_desconto = tipo_desconto
            orcamento.valor_desconto = desconto
            orcamento.taxa_imposto = taxa_imposto
            orcamento.total = total
            await db.commit()
        
        return {
            "subtotal": subtotal,
            "desconto": desconto,
            "imposto": imposto,
            "total": total
        }
