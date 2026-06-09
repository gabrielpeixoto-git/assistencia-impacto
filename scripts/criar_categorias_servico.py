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

# Criar categorias de serviço
categorias = [
    {"nome": "Elétrica", "descricao": "Serviços elétricos em geral", "icone": "zap", "cor": "#FF6B6B", "duracao_padrao_minutos": 60, "preco_minimo": 50.0, "preco_maximo": 5000.0},
    {"nome": "Hidráulica", "descricao": "Serviços hidráulicos em geral", "icone": "droplet", "cor": "#4ECDC4", "duracao_padrao_minutos": 90, "preco_minimo": 80.0, "preco_maximo": 4000.0},
    {"nome": "Pintura", "descricao": "Serviços de pintura", "icone": "palette", "cor": "#96CEB4", "duracao_padrao_minutos": 120, "preco_minimo": 100.0, "preco_maximo": 10000.0},
    {"nome": "Ar Condicionado", "descricao": "Instalação e manutenção de ar condicionado", "icone": "wind", "cor": "#45B7D1", "duracao_padrao_minutos": 60, "preco_minimo": 150.0, "preco_maximo": 3000.0},
    {"nome": "Reparos Gerais", "descricao": "Reparos diversos", "icone": "wrench", "cor": "#F7B731", "duracao_padrao_minutos": 45, "preco_minimo": 30.0, "preco_maximo": 2000.0}
]

print("Criando categorias de serviço...")
for cat in categorias:
    req = urllib.request.Request(
        'http://localhost:8000/api/categorias-servico',
        data=json.dumps(cat).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            print(f"  ✓ {cat['nome']}")
    except urllib.error.HTTPError as e:
        if e.code == 400:
            print(f"  ⚠ {cat['nome']} já existe")
        else:
            print(f"  ✗ Erro ao criar {cat['nome']}: {e.code}")

print("\n✓ Categorias de serviço criadas com sucesso")
