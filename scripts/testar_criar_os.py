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

# Buscar categorias de serviço
print("Buscando categorias de serviço...")
req = urllib.request.Request('http://localhost:8000/api/categorias-servico', headers=headers)
with urllib.request.urlopen(req) as response:
    categorias = json.loads(response.read().decode())
    print(f"  Total de categorias: {len(categorias)}")

# Buscar clientes
print("\nBuscando clientes...")
req = urllib.request.Request('http://localhost:8000/api/clientes', headers=headers)
with urllib.request.urlopen(req) as response:
    clientes = json.loads(response.read().decode())
    print(f"  Total de clientes: {len(clientes)}")

# Buscar usuários (para técnico)
print("\nBuscando usuários...")
req = urllib.request.Request('http://localhost:8000/api/usuarios', headers=headers)
with urllib.request.urlopen(req) as response:
    usuarios = json.loads(response.read().decode())
    admin = next((u for u in usuarios if u["perfil"] == "admin"), None)
    print(f"  Admin encontrado: {admin['nome_completo'] if admin else 'Não'}")

# Criar ordem de serviço
if categorias and clientes and admin:
    print("\nCriando ordem de serviço de teste...")
    os_data = {
        "cliente_id": clientes[0]["id"],
        "tecnico_id": admin["id"],
        "tipo_servico_id": categorias[0]["id"],
        "titulo": "Teste de criação de OS",
        "descricao": "Esta é uma ordem de serviço de teste para verificar se a criação está funcionando",
        "prioridade": "normal",
        "valor_estimado": 500.00
    }
    
    req = urllib.request.Request(
        'http://localhost:8000/api/ordens-servico',
        data=json.dumps(os_data).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            os_criada = json.loads(response.read().decode())
            print(f"  ✓ OS criada com sucesso!")
            print(f"  Número: {os_criada['numero_os']}")
            print(f"  ID: {os_criada['id']}")
    except urllib.error.HTTPError as e:
        print(f"  ✗ Erro ao criar OS: {e.code}")
        print(f"  Detalhes: {e.read().decode()}")
else:
    print("\n✗ Não foi possível criar OS: faltam dados (categorias, clientes ou admin)")
