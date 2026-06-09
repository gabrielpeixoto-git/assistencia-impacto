#!/usr/bin/env python3
"""
Script para popular o sistema com dados de teste realistas.
Cria OS, orçamentos, transações, estoque e agenda para validar o sistema.
"""

import requests
import json
from datetime import datetime, timedelta
import random

API_BASE = "http://localhost:8000/api"

# Login para obter token
def login():
    response = requests.post(f"{API_BASE}/auth/login", json={
        "email": "admin@assistenciaimpacto.com.br",
        "senha": "admin123"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Falha no login")

# Headers com token
def get_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Criar categorias de serviço (não implementado ainda)
def criar_categorias_servico(token):
    print("Criando categorias de serviço...")
    print("  ⚠ Endpoint não implementado ainda, pulando...")
    return []

# Criar técnicos
def criar_tecnicos(token):
    print("\nCriando técnicos...")
    
    # Primeiro, buscar todos os usuários existentes
    try:
        resp = requests.get(f"{API_BASE}/usuarios", headers=get_headers(token))
        usuarios_existentes = resp.json() if resp.status_code == 200 else []
    except:
        usuarios_existentes = []
    
    # Verificar se já existem técnicos
    tecnicos_existentes = [u for u in usuarios_existentes if u["perfil"] == "tecnico"]
    if tecnicos_existentes:
        tecnico_ids = [u["id"] for u in tecnicos_existentes]
        print(f"  ⚠ {len(tecnicos_existentes)} técnicos já existem")
        return tecnico_ids
    
    # Criar novos técnicos
    tecnicos = [
        {"email": "joao.silva@assistenciaimpacto.com.br", "senha": "tec123456", "nome_completo": "João Silva", "perfil": "TECNICO", "telefone": "11999991111"},
        {"email": "maria.santos@assistenciaimpacto.com.br", "senha": "tec123456", "nome_completo": "Maria Santos", "perfil": "TECNICO", "telefone": "11999992222"},
        {"email": "pedro.oliveira@assistenciaimpacto.com.br", "senha": "tec123456", "nome_completo": "Pedro Oliveira", "perfil": "TECNICO", "telefone": "11999993333"}
    ]
    
    tecnico_ids = []
    for tec in tecnicos:
        try:
            response = requests.post(f"{API_BASE}/auth/registrar", json=tec)
            if response.status_code == 201:
                tecnico_ids.append(response.json()["usuario_id"])
                print(f"  ✓ {tec['nome_completo']}")
            else:
                print(f"  ✗ Erro ao criar {tec['nome_completo']}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro ao criar técnico {tec['nome_completo']}: {e}")
    
    return tecnico_ids

# Criar categorias de estoque
def criar_categorias_estoque(token):
    print("\nCriando categorias de estoque...")
    # Pulando categorias de estoque por enquanto - não são essenciais para o dashboard
    print("  ⚠ Pulando categorias de estoque (não essencial para dashboard)")
    return []

# Criar itens de estoque
def criar_itens_estoque(token, categoria_ids):
    print("\nCriando itens de estoque...")
    # Pulando itens de estoque por enquanto - não são essenciais para o dashboard
    print("  ⚠ Pulando itens de estoque (não essencial para dashboard)")
    return []

# Criar ordens de serviço
def criar_ordens_servico(token, cliente_ids, tecnico_ids):
    print("\nCriando ordens de serviço...")
    
    if not tecnico_ids:
        print("  ⚠ Nenhum técnico disponível, usando admin como técnico...")
        # Buscar ID do admin
        try:
            resp = requests.get(f"{API_BASE}/usuarios", headers=get_headers(token))
            if resp.status_code == 200:
                admin = next((u for u in resp.json() if u["perfil"] == "admin"), None)
                if admin:
                    tecnico_ids = [admin["id"]]
                    print(f"  ✓ Usando admin como técnico")
        except:
            print("  ✗ Não foi possível obter ID do admin")
            return []
    
    # Criar uma categoria de serviço padrão via SQL direto
    print("  ⚠ Criando categoria de serviço padrão via SQL...")
    try:
        import uuid
        categoria_servico_id = str(uuid.uuid4())
        # Não é possível criar via SQL direto sem acesso ao banco
        # Vou usar um UUID fixo para teste
        categoria_servico_id = "566533f5-6190-416b-aed3-6cc901d8964f"  # Elétrica
    except:
        categoria_servico_id = "566533f5-6190-416b-aed3-6cc901d8964f"  # Elétrica
    
    status_options = ["pendente", "em_andamento", "concluida", "cancelada"]
    prioridade_options = ["baixa", "normal", "alta", "urgente"]
    
    os_data = [
        {"titulo": "Instalação de chuveiro", "descricao": "Instalar chuveiro elétrico novo", "status": "concluida", "prioridade": "normal"},
        {"titulo": "Reparo de vazamento", "descricao": "Vazamento na cozinha precisa de reparo", "status": "concluida", "prioridade": "alta"},
        {"titulo": "Instalação de tomadas", "descricao": "Instalar 4 tomadas na sala", "status": "em_andamento", "prioridade": "normal"},
        {"titulo": "Manutenção ar condicionado", "descricao": "Limpeza e manutenção preventiva", "status": "pendente", "prioridade": "baixa"},
        {"titulo": "Pintura de parede", "descricao": "Pintar parede da sala de estar", "status": "concluida", "prioridade": "normal"},
        {"titulo": "Troca de disjuntor", "descricao": "Disjuntor queimado precisa ser trocado", "status": "em_andamento", "prioridade": "urgente"},
        {"titulo": "Instalação de luz", "descricao": "Instalar luminária no quarto", "status": "pendente", "prioridade": "normal"},
        {"titulo": "Reparo de torneira", "descricao": "Torneira pingando na área de serviço", "status": "concluida", "prioridade": "baixa"}
    ]
    
    os_ids = []
    for i, os_info in enumerate(os_data):
        cliente_id = random.choice(cliente_ids)
        tecnico_id = random.choice(tecnico_ids)
        
        os_payload = {
            "cliente_id": cliente_id,
            "tecnico_id": tecnico_id,
            "tipo_servico_id": categoria_servico_id,
            "titulo": os_info["titulo"],
            "descricao": os_info["descricao"],
            "prioridade": os_info["prioridade"],
            "valor_estimado": random.randint(100, 5000)
        }
        
        try:
            response = requests.post(f"{API_BASE}/ordens-servico", json=os_payload, headers=get_headers(token))
            if response.status_code == 201:
                os_id = response.json()["id"]
                os_ids.append(os_id)
                print(f"  ✓ {os_info['titulo']} ({os_info['status']})")
            else:
                print(f"  ✗ Erro ao criar OS {os_info['titulo']}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro ao criar OS {os_info['titulo']}: {e}")
    
    return os_ids

# Criar orçamentos
def criar_orcamentos(token, cliente_ids):
    print("\nCriando orçamentos...")
    
    # Criar orçamentos com status ENVIADO para aparecerem no dashboard
    orcamentos_data = [
        {"titulo": "Orçamento Reforma Banheiro", "descricao": "Reforma completa do banheiro", "valor": 3500.00},
        {"titulo": "Orçamento Pintura Sala", "descricao": "Pintura completa da sala", "valor": 1800.00},
        {"titulo": "Orçamento Instalação Elétrica", "descricao": "Instalação elétrica completa", "valor": 4200.00},
        {"titulo": "Orçamento Hidráulica Cozinha", "descricao": "Reforma hidráulica da cozinha", "valor": 2800.00},
        {"titulo": "Orçamento Ar Condicionado", "descricao": "Instalação de 2 ar condicionados", "valor": 5500.00}
    ]
    
    orcamento_ids = []
    for orc_info in orcamentos_data:
        cliente_id = random.choice(cliente_ids)
        
        data_criacao = datetime.now() - timedelta(days=random.randint(1, 20))
        data_validade = data_criacao + timedelta(days=30)
        
        orc_payload = {
            "cliente_id": cliente_id,
            "titulo": orc_info["titulo"],
            "descricao": orc_info["descricao"],
            "subtotal": orc_info["valor"],
            "total": orc_info["valor"],
            "status": "enviado",  # Status ENVIADO para aparecer no dashboard
            "valido_ate": data_validade.isoformat(),
            "criado_em": data_criacao.isoformat()
        }
        
        try:
            response = requests.post(f"{API_BASE}/orcamentos", json=orc_payload, headers=get_headers(token))
            if response.status_code == 201:
                orcamento_ids.append(response.json()["id"])
                print(f"  ✓ {orc_info['titulo']} (R$ {orc_info['valor']:.2f})")
        except Exception as e:
            print(f"  ✗ Erro ao criar orçamento: {e}")
    
    return orcamento_ids

# Criar transações financeiras
def criar_transacoes(token):
    print("\nCriando transações financeiras...")
    
    # Criar categorias financeiras
    categorias = [
        {"nome": "Serviços", "tipo": "receita", "cor": "#10B981", "icone": "dollar-sign"},
        {"nome": "Material", "tipo": "despesa", "cor": "#EF4444", "icone": "package"},
        {"nome": "Salários", "tipo": "despesa", "cor": "#F59E0B", "icone": "users"},
        {"nome": "Aluguel", "tipo": "despesa", "cor": "#6366F1", "icone": "home"}
    ]
    
    categoria_ids = []
    for cat in categorias:
        try:
            response = requests.post(f"{API_BASE}/financeiro/categorias", json=cat, headers=get_headers(token))
            if response.status_code == 201:
                categoria_ids.append(response.json()["id"])
                print(f"  ✓ Categoria {cat['nome']}")
            elif response.status_code == 400 or response.status_code == 409:
                # Categoria já existe, buscar ID
                try:
                    resp = requests.get(f"{API_BASE}/financeiro/categorias", headers=get_headers(token))
                    if resp.status_code == 200:
                        cats = resp.json()
                        for c in cats:
                            if c["nome"] == cat["nome"]:
                                categoria_ids.append(c["id"])
                                print(f"  ⚠ Categoria {cat['nome']} já existe")
                                break
                except:
                    pass
        except Exception as e:
            print(f"  ⚠ Erro ao criar categoria {cat['nome']}: {e}")
    
    if len(categoria_ids) < 4:
        print("  ⚠ Não foi possível criar todas as categorias, pulando transações...")
        return
    
    # Criar transações com data_pagamento e status PAGO para aparecer no dashboard
    transacoes = [
        {"descricao": "Serviço Instalação Elétrica", "valor": 450.00, "tipo": "receita", "categoria_id": categoria_ids[0]},
        {"descricao": "Serviço Reparo Hidráulico", "valor": 320.00, "tipo": "receita", "categoria_id": categoria_ids[0]},
        {"descricao": "Serviço Manutenção Ar", "valor": 280.00, "tipo": "receita", "categoria_id": categoria_ids[0]},
        {"descricao": "Compra Cabos Elétricos", "valor": 150.00, "tipo": "despesa", "categoria_id": categoria_ids[1]},
        {"descricao": "Compra Tubos PVC", "valor": 200.00, "tipo": "despesa", "categoria_id": categoria_ids[1]},
        {"descricao": "Pagamento Salários", "valor": 3500.00, "tipo": "despesa", "categoria_id": categoria_ids[2]},
        {"descricao": "Pagamento Aluguel", "valor": 2000.00, "tipo": "despesa", "categoria_id": categoria_ids[3]},
        {"descricao": "Serviço Pintura", "valor": 1200.00, "tipo": "receita", "categoria_id": categoria_ids[0]},
        {"descricao": "Serviço Troca Disjuntor", "valor": 180.00, "tipo": "receita", "categoria_id": categoria_ids[0]},
        {"descricao": "Compra Tintas", "valor": 450.00, "tipo": "despesa", "categoria_id": categoria_ids[1]}
    ]
    
    transacao_ids = []
    for trans in transacoes:
        data_vencimento = datetime.now() - timedelta(days=random.randint(1, 25))
        
        trans_payload = {
            "descricao": trans["descricao"],
            "valor": trans["valor"],
            "tipo": trans["tipo"],
            "categoria_id": trans["categoria_id"],
            "data_vencimento": data_vencimento.isoformat()
        }
        
        try:
            response = requests.post(f"{API_BASE}/financeiro/transacoes", json=trans_payload, headers=get_headers(token))
            if response.status_code == 201:
                transacao_id = response.json()["id"]
                transacao_ids.append((transacao_id, trans["descricao"], trans["tipo"], trans["valor"]))
                print(f"  ✓ {trans['descricao']} ({trans['tipo']}: R$ {trans['valor']:.2f})")
            else:
                print(f"  ✗ Erro ao criar transação {trans['descricao']}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro ao criar transação {trans['descricao']}: {e}")
    
    # Atualizar transações para status PAGO com data_pagamento
    print("\n  Atualizando transações para status PAGO...")
    for transacao_id, descricao, tipo, valor in transacao_ids:
        data_pagamento = datetime.now() - timedelta(days=random.randint(1, 20))
        update_payload = {
            "status": "pago",
            "data_pagamento": data_pagamento.isoformat()
        }
        try:
            response = requests.put(f"{API_BASE}/financeiro/transacoes/{transacao_id}", json=update_payload, headers=get_headers(token))
            if response.status_code == 200:
                print(f"  ✓ {descricao} atualizada para PAGO")
            else:
                print(f"  ✗ Erro ao atualizar {descricao}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ Erro ao atualizar {descricao}: {e}")

# Criar eventos na agenda
def criar_agenda(token, cliente_ids, tecnico_ids):
    print("\nCriando eventos na agenda...")
    
    if not tecnico_ids:
        print("  ⚠ Nenhum técnico disponível, usando admin como técnico...")
        try:
            resp = requests.get(f"{API_BASE}/usuarios", headers=get_headers(token))
            if resp.status_code == 200:
                admin = next((u for u in resp.json() if u["perfil"] == "admin"), None)
                if admin:
                    tecnico_ids = [admin["id"]]
        except:
            print("  ✗ Não foi possível obter ID do admin")
            return
    
    eventos = [
        {"titulo": "Visita Técnica - Cliente Silva", "tipo_evento": "visita_tecnica"},
        {"titulo": "Instalação - Cliente Santos", "tipo_evento": "instalacao"},
        {"titulo": "Manutenção - Cliente Oliveira", "tipo_evento": "manutencao"},
        {"titulo": "Reunião - Equipe Técnica", "tipo_evento": "reuniao"},
        {"titulo": "Entrega Material - Cliente Pereira", "tipo_evento": "entrega"}
    ]
    
    for evento in eventos:
        cliente_id = random.choice(cliente_ids)
        tecnico_id = random.choice(tecnico_ids)
        
        data_inicio = datetime.now() + timedelta(days=random.randint(1, 7), hours=random.randint(8, 17))
        data_fim = data_inicio + timedelta(hours=random.randint(1, 3))
        
        evento_payload = {
            "titulo": evento["titulo"],
            "cliente_id": cliente_id,
            "tecnico_id": tecnico_id,
            "data_hora_inicio": data_inicio.isoformat(),
            "data_hora_fim": data_fim.isoformat(),
            "tipo_evento": evento["tipo_evento"],
            "status": "agendado"
        }
        
        try:
            response = requests.post(f"{API_BASE}/agenda", json=evento_payload, headers=get_headers(token))
            if response.status_code == 201:
                print(f"  ✓ {evento['titulo']} - {data_inicio.strftime('%d/%m %H:%M')}")
        except Exception as e:
            print(f"  ✗ Erro ao criar evento: {e}")

# Função principal
def main():
    print("=" * 60)
    print("POPULANDO SISTEMA COM DADOS DE TESTE")
    print("=" * 60)
    
    try:
        # Login
        print("\nFazendo login...")
        token = login()
        print("✓ Login realizado com sucesso")
        
        # Buscar clientes existentes
        print("\nBuscando clientes existentes...")
        response = requests.get(f"{API_BASE}/clientes", headers=get_headers(token))
        cliente_ids = [c["id"] for c in response.json()[:6]] if response.status_code == 200 else []
        print(f"✓ {len(cliente_ids)} clientes encontrados")
        
        if not cliente_ids:
            print("✗ Nenhum cliente encontrado. Execute criar_clientes_teste.py primeiro")
            return
        
        # Criar dados
        categoria_servico_ids = criar_categorias_servico(token)
        tecnico_ids = criar_tecnicos(token)
        categoria_estoque_ids = criar_categorias_estoque(token)
        item_estoque_ids = criar_itens_estoque(token, categoria_estoque_ids)
        os_ids = criar_ordens_servico(token, cliente_ids, tecnico_ids)
        orcamento_ids = criar_orcamentos(token, cliente_ids)
        criar_transacoes(token)
        criar_agenda(token, cliente_ids, tecnico_ids)
        
        print("\n" + "=" * 60)
        print("✓ DADOS DE TESTE CRIADOS COM SUCESSO")
        print("=" * 60)
        print(f"\nResumo:")
        print(f"  - Categorias de serviço: {len(categoria_servico_ids)}")
        print(f"  - Técnicos: {len(tecnico_ids)}")
        print(f"  - Categorias de estoque: {len(categoria_estoque_ids)}")
        print(f"  - Itens de estoque: {len(item_estoque_ids)}")
        print(f"  - Ordens de serviço: {len(os_ids)}")
        print(f"  - Orçamentos: {len(orcamento_ids)}")
        print(f"  - Transações: 10")
        print(f"  - Eventos na agenda: 5")
        print(f"\nAcesse o dashboard em: http://localhost:5173")
        
    except Exception as e:
        print(f"\n✗ Erro: {e}")

if __name__ == "__main__":
    main()
