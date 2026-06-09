"""
Script para criar dados de teste para relatórios em diferentes períodos.
Cria transações, ordens de serviço e orçamentos com datas variadas.
"""
import urllib.request
import json
from datetime import datetime, timedelta

# Obter token
req = urllib.request.Request(
    'http://localhost:8000/api/auth/login',
    data=json.dumps({'email': 'admin@assistenciaimpacto.com.br', 'senha': 'admin123'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
    token = data['access_token']
    print(f"Token obtido: {token[:50]}...")

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Buscar clientes existentes
req = urllib.request.Request(
    'http://localhost:8000/api/clientes?limit=5',
    headers=headers,
    method='GET'
)
with urllib.request.urlopen(req) as response:
    clientes_data = json.loads(response.read().decode())
    clientes = clientes_data
    print(f"\n{len(clientes)} clientes encontrados")

if not clientes:
    print("ERRO: Nenhum cliente encontrado. Execute criar_clientes_teste.py primeiro.")
    exit(1)

# Buscar categorias financeiras
req = urllib.request.Request(
    'http://localhost:8000/api/financeiro/categorias',
    headers=headers,
    method='GET'
)
with urllib.request.urlopen(req) as response:
    categorias = json.loads(response.read().decode())
    cat_receita = next((c for c in categorias if c['tipo'] == 'receita'), None)
    cat_despesa = next((c for c in categorias if c['tipo'] == 'despesa'), None)
    print(f"Categorias: receita={cat_receita['nome'] if cat_receita else None}, despesa={cat_despesa['nome'] if cat_despesa else None}")

# Buscar categorias de serviço
req = urllib.request.Request(
    'http://localhost:8000/api/categorias-servico?limit=1',
    headers=headers,
    method='GET'
)
with urllib.request.urlopen(req) as response:
    cats_servico = json.loads(response.read().decode())
    cat_servico = cats_servico[0] if cats_servico else None
    print(f"Categoria de serviço: {cat_servico['nome'] if cat_servico else None}")

# Buscar usuário para usar como técnico
req = urllib.request.Request(
    'http://localhost:8000/api/usuarios/?limit=1',
    headers=headers,
    method='GET'
)
with urllib.request.urlopen(req) as response:
    usuarios = json.loads(response.read().decode())
    tecnico_id = usuarios[0]['id'] if usuarios else clientes[0]['id']
    print(f"Usando técnico ID: {tecnico_id}")

hoje = datetime.now()

# Função para formatar data para API
def formatar_data(data):
    return data.isoformat()

# Criar dados para HOJE
print("\n=== Criando dados para HOJE ===")
for i in range(3):
    # Transação receita hoje
    transacao_receita = {
        'numero_transacao': f'TRXHOJE{i}',
        'tipo': 'receita',
        'status': 'pago',
        'valor': 1000 + (i * 500),
        'descricao': f'Receita teste hoje {i}',
        'data_vencimento': formatar_data(hoje),
        'data_pagamento': formatar_data(hoje),
        'categoria_id': cat_receita['id'] if cat_receita else None,
        'cliente_id': clientes[i % len(clientes)]['id']
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/financeiro/transacoes',
        data=json.dumps(transacao_receita).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Transação receita {i} criada")
    
    # Transação despesa hoje
    transacao_despesa = {
        'numero_transacao': f'TRXDESPHOJE{i}',
        'tipo': 'despesa',
        'status': 'pago',
        'valor': 500 + (i * 200),
        'descricao': f'Despesa teste hoje {i}',
        'data_vencimento': formatar_data(hoje),
        'data_pagamento': formatar_data(hoje),
        'categoria_id': cat_despesa['id'] if cat_despesa else None
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/financeiro/transacoes',
        data=json.dumps(transacao_despesa).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Transação despesa {i} criada")
    
    # Ordem de serviço hoje
    os_hoje = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'tecnico_id': tecnico_id,
        'tipo_servico_id': cat_servico['id'] if cat_servico else None,
        'titulo': f'OS teste hoje {i}',
        'descricao': f'Descrição OS teste hoje {i}',
        'prioridade': 'normal',
        'valor_estimado': 2000 + (i * 1000),
        'valor_final': 2000 + (i * 1000),
        'status': 'concluida' if i % 2 == 0 else 'em_andamento'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/ordens-servico',
        data=json.dumps(os_hoje).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  OS {i} criada")
    
    # Orçamento hoje
    orcamento_hoje = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'titulo': f'Orçamento teste hoje {i}',
        'descricao': f'Descrição orçamento teste hoje {i}',
        'valor_total': 1500 + (i * 500),
        'status': 'aprovado' if i % 2 == 0 else 'enviado'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/orcamentos',
        data=json.dumps(orcamento_hoje).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Orçamento {i} criado")

# Criar dados para ESTA SEMANA (2 dias atrás)
print("\n=== Criando dados para ESTA SEMANA (2 dias atrás) ===")
dias_atras = 2
data_semana = hoje - timedelta(days=dias_atras)
for i in range(3):
    transacao_receita = {
        'numero_transacao': f'TRXSEM{i}',
        'tipo': 'receita',
        'status': 'pago',
        'valor': 2000 + (i * 700),
        'descricao': f'Receita teste semana {i}',
        'data_vencimento': formatar_data(data_semana),
        'data_pagamento': formatar_data(data_semana),
        'categoria_id': cat_receita['id'] if cat_receita else None,
        'cliente_id': clientes[i % len(clientes)]['id']
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/financeiro/transacoes',
        data=json.dumps(transacao_receita).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Transação receita {i} criada")
    
    os_semana = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'tecnico_id': tecnico_id,
        'tipo_servico_id': cat_servico['id'] if cat_servico else None,
        'titulo': f'OS teste semana {i}',
        'descricao': f'Descrição OS teste semana {i}',
        'prioridade': 'normal',
        'valor_estimado': 3000 + (i * 1500),
        'valor_final': 3000 + (i * 1500),
        'status': 'concluida'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/ordens-servico',
        data=json.dumps(os_semana).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  OS {i} criada")
    
    orcamento_semana = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'titulo': f'Orçamento teste semana {i}',
        'descricao': f'Descrição orçamento teste semana {i}',
        'valor_total': 2500 + (i * 800),
        'status': 'aprovado'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/orcamentos',
        data=json.dumps(orcamento_semana).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Orçamento {i} criado")

# Criar dados para ESTE MÊS (10 dias atrás)
print("\n=== Criando dados para ESTE MÊS (10 dias atrás) ===")
dias_atras = 10
data_mes = hoje - timedelta(days=dias_atras)
for i in range(4):
    transacao_receita = {
        'numero_transacao': f'TRXMES{i}',
        'tipo': 'receita',
        'status': 'pago',
        'valor': 3000 + (i * 1000),
        'descricao': f'Receita teste mês {i}',
        'data_vencimento': formatar_data(data_mes),
        'data_pagamento': formatar_data(data_mes),
        'categoria_id': cat_receita['id'] if cat_receita else None,
        'cliente_id': clientes[i % len(clientes)]['id']
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/financeiro/transacoes',
        data=json.dumps(transacao_receita).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Transação receita {i} criada")
    
    transacao_despesa = {
        'numero_transacao': f'TRXDESPMES{i}',
        'tipo': 'despesa',
        'status': 'pago',
        'valor': 1500 + (i * 500),
        'descricao': f'Despesa teste mês {i}',
        'data_vencimento': formatar_data(data_mes),
        'data_pagamento': formatar_data(data_mes),
        'categoria_id': cat_despesa['id'] if cat_despesa else None
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/financeiro/transacoes',
        data=json.dumps(transacao_despesa).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Transação despesa {i} criada")
    
    os_mes = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'tecnico_id': tecnico_id,
        'tipo_servico_id': cat_servico['id'] if cat_servico else None,
        'titulo': f'OS teste mês {i}',
        'descricao': f'Descrição OS teste mês {i}',
        'prioridade': 'normal',
        'valor_estimado': 4000 + (i * 2000),
        'valor_final': 4000 + (i * 2000),
        'status': 'concluida'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/ordens-servico',
        data=json.dumps(os_mes).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  OS {i} criada")
    
    orcamento_mes = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'titulo': f'Orçamento teste mês {i}',
        'descricao': f'Descrição orçamento teste mês {i}',
        'valor_total': 3500 + (i * 1000),
        'status': 'aprovado' if i % 2 == 0 else 'recusado'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/orcamentos',
        data=json.dumps(orcamento_mes).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Orçamento {i} criado")

# Criar dados para ESTE TRIMESTRE (40 dias atrás)
print("\n=== Criando dados para ESTE TRIMESTRE (40 dias atrás) ===")
dias_atras = 40
data_trimestre = hoje - timedelta(days=dias_atras)
for i in range(3):
    transacao_receita = {
        'numero_transacao': f'TRXTRI{i}',
        'tipo': 'receita',
        'status': 'pago',
        'valor': 5000 + (i * 2000),
        'descricao': f'Receita teste trimestre {i}',
        'data_vencimento': formatar_data(data_trimestre),
        'data_pagamento': formatar_data(data_trimestre),
        'categoria_id': cat_receita['id'] if cat_receita else None,
        'cliente_id': clientes[i % len(clientes)]['id']
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/financeiro/transacoes',
        data=json.dumps(transacao_receita).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Transação receita {i} criada")
    
    os_trimestre = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'tecnico_id': tecnico_id,
        'tipo_servico_id': cat_servico['id'] if cat_servico else None,
        'titulo': f'OS teste trimestre {i}',
        'descricao': f'Descrição OS teste trimestre {i}',
        'prioridade': 'normal',
        'valor_estimado': 6000 + (i * 3000),
        'valor_final': 6000 + (i * 3000),
        'status': 'concluida'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/ordens-servico',
        data=json.dumps(os_trimestre).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  OS {i} criada")
    
    orcamento_trimestre = {
        'cliente_id': clientes[i % len(clientes)]['id'],
        'titulo': f'Orçamento teste trimestre {i}',
        'descricao': f'Descrição orçamento teste trimestre {i}',
        'valor_total': 5500 + (i * 2000),
        'status': 'aprovado'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/orcamentos',
        data=json.dumps(orcamento_trimestre).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    with urllib.request.urlopen(req) as response:
        print(f"  Orçamento {i} criado")

print("\n=== Dados de teste criados com sucesso ===")
print("Resumo:")
print("- 3 transações receita + 3 despesas para HOJE")
print("- 3 transações receita para ESTA SEMANA (2 dias atrás)")
print("- 4 transações receita + 4 despesas para ESTE MÊS (10 dias atrás)")
print("- 3 transações receita para ESTE TRIMESTRE (40 dias atrás)")
print("- Ordens de serviço e orçamentos para cada período")
