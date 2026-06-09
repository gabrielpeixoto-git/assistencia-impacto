import urllib.request
import json

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

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Testar listar ordens de serviço
print("Testando listar ordens de serviço...")
req = urllib.request.Request('http://localhost:8000/api/ordens-servico', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        ordens = json.loads(response.read().decode())
        print(f"  ✓ Total de ordens: {len(ordens)}")
        for os in ordens[:3]:
            print(f"    - {os['numero_os']}: {os['titulo']}")
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")

# Testar buscar categorias de serviço
print("\nTestando buscar categorias de serviço...")
req = urllib.request.Request('http://localhost:8000/api/categorias-servico', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        categorias = json.loads(response.read().decode())
        print(f"  ✓ Total de categorias: {len(categorias)}")
        categoria_id = categorias[0]['id'] if categorias else None
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")
    categoria_id = None

# Testar buscar clientes
print("\nTestando buscar clientes...")
req = urllib.request.Request('http://localhost:8000/api/clientes', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        clientes = json.loads(response.read().decode())
        print(f"  ✓ Total de clientes: {len(clientes)}")
        cliente_id = clientes[0]['id'] if clientes else None
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")
    cliente_id = None

# Testar buscar usuários
print("\nTestando buscar usuários...")
req = urllib.request.Request('http://localhost:8000/api/usuarios', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        usuarios = json.loads(response.read().decode())
        print(f"  ✓ Total de usuários: {len(usuarios)}")
        tecnico_id = usuarios[0]['id'] if usuarios else None
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")
    tecnico_id = None

# Testar criar ordem de serviço com todos os campos
if cliente_id and categoria_id and tecnico_id:
    print("\n=== Testando criar ordem de serviço ===")
    nova_os = {
        'cliente_id': cliente_id,
        'tecnico_id': tecnico_id,
        'tipo_servico_id': categoria_id,
        'titulo': 'OS Teste Edição',
        'descricao': 'Descrição detalhada da ordem de serviço para teste de edição',
        'prioridade': 'normal',
        'valor_estimado': 500.0,
        'data_agendada': '2026-05-25T10:00:00',
        'status': 'pendente',
        'observacoes_internas': 'Observações internas para teste',
        'endereco_id': None,
        'forma_pagamento': 'dinheiro',
        'emitir_nota': True
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/ordens-servico',
        data=json.dumps(nova_os).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            os_criada = json.loads(response.read().decode())
            print(f"  ✓ OS criada: {os_criada['numero_os']}")
            os_id = os_criada['id']

            # Testar atualizar OS com campos corrigidos
            print("\n=== Testando atualizar OS com campos corrigidos ===")
            os_atualizada = {
                'cliente_id': cliente_id,
                'tipo_servico_id': categoria_id,
                'titulo': 'OS Teste Edição - Atualizada',
                'descricao': 'Descrição atualizada',
                'observacoes_internas': 'Observações atualizadas',
                'endereco_id': None,
                'forma_pagamento': 'cartao_credito',
                'emitir_nota': False
            }
            req = urllib.request.Request(
                f'http://localhost:8000/api/ordens-servico/{os_id}',
                data=json.dumps(os_atualizada).encode('utf-8'),
                headers=headers,
                method='PUT'
            )
            with urllib.request.urlopen(req) as response:
                os = json.loads(response.read().decode())
                print(f"  ✓ OS atualizada: {os['numero_os']}")
                # Verificar campos corrigidos
                assert os['observacoes_internas'] == 'Observações atualizadas', "observacoes_internas não foi atualizado"
                assert os['forma_pagamento'] == 'cartao_credito', "forma_pagamento não foi atualizado"
                assert os['emitir_nota'] == False, "emitir_nota não foi atualizado"
                print("  ✓ Campos corrigidos atualizados com sucesso!")
    except urllib.error.HTTPError as e:
        print(f"  ✗ Erro: {e.code}")
        print(f"  Detalhes: {e.read().decode()}")
else:
    print("\n⚠ Não foi possível testar criação/atualização de OS (falta cliente, categoria ou técnico)")

print("\n=== Testes concluídos ===")
