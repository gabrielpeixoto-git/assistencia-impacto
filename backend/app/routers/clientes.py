from typing import List
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.schemas.cliente import ClienteCreate, ClienteUpdate, ClienteResponse, EnderecoClienteCreate
from app.models.cliente import Cliente, EnderecoCliente
from app.dependencies import get_usuario_atual
from app.models.usuario import Usuario
from loguru import logger
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.get("", response_model=List[ClienteResponse])
async def listar_clientes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    busca: str = None,
    tipo_cliente: str = None,
    ativo: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os clientes com filtros opcionais."""
    query = select(Cliente)
    
    if busca:
        query = query.where(Cliente.nome.ilike(f"%{busca}%"))
    
    if tipo_cliente:
        query = query.where(Cliente.tipo_cliente == tipo_cliente)
    
    if ativo is not None:
        query = query.where(Cliente.ativo == ativo)
    
    query = query.order_by(Cliente.nome).offset(skip).limit(limit)
    result = await db.execute(query)
    clientes = result.scalars().all()
    
    return clientes


@router.get("/{cliente_id}", response_model=ClienteResponse)
async def obter_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Obtém um cliente específico por ID."""
    query = select(Cliente).where(Cliente.id == cliente_id)
    result = await db.execute(query)
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente
    

@router.post("", response_model=ClienteResponse, status_code=201)
async def criar_cliente(
    cliente_data: ClienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Cria um novo cliente."""
    try:
        cliente = Cliente(
            **cliente_data.model_dump(),
            criado_por=current_user.id
        )
        
        db.add(cliente)
        await db.commit()
        await db.refresh(cliente)
        
        logger.info(f"Cliente {cliente.nome} (ID: {cliente.id}) criado por {current_user.email}")
        return cliente
    except Exception as e:
        logger.error(f"Erro ao criar cliente {cliente_data.nome}: {str(e)}")
        raise


@router.put("/{cliente_id}", response_model=ClienteResponse)
async def atualizar_cliente(
    cliente_id: str,
    cliente_data: ClienteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Atualiza um cliente existente."""
    try:
        query = select(Cliente).where(Cliente.id == cliente_id)
        result = await db.execute(query)
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            logger.warning(f"Cliente {cliente_id} não encontrado para atualização por {current_user.email}")
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        update_data = cliente_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(cliente, field, value)
        
        await db.commit()
        await db.refresh(cliente)
        
        logger.info(f"Cliente {cliente.nome} (ID: {cliente_id}) atualizado por {current_user.email}")
        return cliente
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar cliente {cliente_id}: {str(e)}")
        raise


@router.delete("/{cliente_id}", status_code=204)
async def deletar_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Deleta um cliente (soft delete)."""
    try:
        query = select(Cliente).where(Cliente.id == cliente_id)
        result = await db.execute(query)
        cliente = result.scalar_one_or_none()
        
        if not cliente:
            logger.warning(f"Cliente {cliente_id} não encontrado para deleção por {current_user.email}")
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        cliente.ativo = False
        await db.commit()
        
        logger.info(f"Cliente {cliente.nome} (ID: {cliente_id}) desativado por {current_user.email}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar cliente {cliente_id}: {str(e)}")
        raise


@router.post("/{cliente_id}/enderecos", response_model=dict, status_code=201)
async def adicionar_endereco_cliente(
    cliente_id: str,
    endereco_data: EnderecoClienteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Adiciona um endereço adicional a um cliente."""
    # Verificar se o cliente existe
    query = select(Cliente).where(Cliente.id == cliente_id)
    result = await db.execute(query)
    cliente = result.scalar_one_or_none()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    # Se for endereço padrão, remover padrão dos outros
    if endereco_data.padrao:
        query_padrao = select(EnderecoCliente).where(
            and_(
                EnderecoCliente.cliente_id == cliente_id,
                EnderecoCliente.padrao == True
            )
        )
        result_padrao = await db.execute(query_padrao)
        enderecos_padrao = result_padrao.scalars().all()
        
        for endereco in enderecos_padrao:
            endereco.padrao = False
    
    endereco = EnderecoCliente(
        cliente_id=cliente_id,
        **endereco_data.model_dump()
    )
    
    db.add(endereco)
    await db.commit()
    await db.refresh(endereco)
    
    return {"id": endereco.id, "mensagem": "Endereço adicionado com sucesso"}


@router.get("/{cliente_id}/enderecos", response_model=List[dict])
async def listar_enderecos_cliente(
    cliente_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_usuario_atual)
):
    """Lista todos os endereços de um cliente."""
    query = select(EnderecoCliente).where(EnderecoCliente.cliente_id == cliente_id)
    result = await db.execute(query)
    enderecos = result.scalars().all()
    
    return [
        {
            "id": e.id,
            "rotulo": e.rotulo,
            "logradouro": e.logradouro,
            "numero": e.numero,
            "complemento": e.complemento,
            "bairro": e.bairro,
            "cidade": e.cidade,
            "estado": e.estado,
            "cep": e.cep,
            "padrao": e.padrao,
            "latitude": e.latitude,
            "longitude": e.longitude
        }
        for e in enderecos
    ]


@router.get("/buscar-endereco")
async def buscar_endereco_por_cep(
    cep: str = Query(..., description="CEP para busca")
):
    """Busca endereço pelo CEP usando ViaCEP."""
    cep_limpo = ''.join(filter(str.isdigit, cep))
    if len(cep_limpo) != 8:
        raise HTTPException(status_code=400, detail="CEP inválido — deve ter 8 dígitos")

    async with httpx.AsyncClient() as http_client:
        try:
            response = await http_client.get(
                f"https://viacep.com.br/ws/{cep_limpo}/json/",
                timeout=5.0
            )
            data = response.json()
            if "erro" in data:
                raise HTTPException(status_code=404, detail="CEP não encontrado")
            return {
                "sucesso": True,
                "dados": {
                    "logradouro": data.get("logradouro", ""),
                    "bairro": data.get("bairro", ""),
                    "cidade": data.get("localidade", ""),
                    "estado": data.get("uf", ""),
                    "cep": cep_limpo
                }
            }
        except httpx.TimeoutException:
            raise HTTPException(status_code=503, detail="Serviço ViaCEP indisponível. Tente novamente.")
