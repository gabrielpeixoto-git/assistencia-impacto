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
    print(f"Token obtido: {token[:50]}...")

headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# Testar buscar categorias de estoque
print("\n=== Buscando categorias de estoque ===")
req = urllib.request.Request('http://localhost:8000/api/estoque/categorias', headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        categorias = json.loads(response.read().decode())
        print(f"  ✓ Total de categorias: {len(categorias)}")
        categoria_id = categorias[0]['id'] if categorias else None
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")
    categoria_id = None

if not categoria_id:
    print("\n⚠ Criando categoria de estoque para teste...")
    nova_categoria = {
        'nome': 'Categoria Teste',
        'cor': '#FF0000',
        'icone': 'package'
    }
    req = urllib.request.Request(
        'http://localhost:8000/api/estoque/categorias',
        data=json.dumps(nova_categoria).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    try:
        with urllib.request.urlopen(req) as response:
            categoria = json.loads(response.read().decode())
            categoria_id = categoria['id']
            print(f"  ✓ Categoria criada: {categoria['nome']}")
    except urllib.error.HTTPError as e:
        print(f"  ✗ Erro ao criar categoria: {e.code}")
        print(f"  Detalhes: {e.read().decode()}")
        exit(1)

# Testar criar item de estoque com SKU
print("\n=== Criando item de estoque ===")
novo_item = {
    'sku': 'SKU-TEST-001',
    'nome': 'Item Teste Edição',
    'descricao': 'Descrição do item para teste de edição',
    'categoria_id': categoria_id,
    'unidade': 'unidade',
    'estoque_minimo': 10.0,
    'estoque_maximo': 100.0,
    'custo_unitario': 50.0,
    'preco_venda': 100.0,
    'percentual_markup': 100.0,
    'fornecedor': 'Fornecedor Teste',
    'codigo_fornecedor': 'COD-FORN-001',
    'codigo_barras': '7891234567890',
    'localizacao_estoque': 'Prateleira A'
}
req = urllib.request.Request(
    'http://localhost:8000/api/estoque/itens',
    data=json.dumps(novo_item).encode('utf-8'),
    headers=headers,
    method='POST'
)
try:
    with urllib.request.urlopen(req) as response:
        item_criado = json.loads(response.read().decode())
        print(f"  ✓ Item criado: {item_criado['nome']} (SKU: {item_criado['sku']})")
        item_id = item_criado['id']
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")
    exit(1)

# Testar atualizar item com SKU corrigido
print("\n=== Atualizando item com SKU corrigido ===")
item_atualizado = {
    'sku': 'SKU-TEST-002',
    'nome': 'Item Teste Edição - Atualizado',
    'descricao': 'Descrição atualizada',
    'estoque_minimo': 15.0,
    'preco_venda': 120.0
}
req = urllib.request.Request(
    f'http://localhost:8000/api/estoque/itens/{item_id}',
    data=json.dumps(item_atualizado).encode('utf-8'),
    headers=headers,
    method='PUT'
)
try:
    with urllib.request.urlopen(req) as response:
        item = json.loads(response.read().decode())
        print(f"  ✓ Item atualizado: {item['nome']} (SKU: {item['sku']})")
        # Verificar se o SKU foi atualizado
        assert item['sku'] == 'SKU-TEST-002', "SKU não foi atualizado"
        assert item['nome'] == 'Item Teste Edição - Atualizado', "nome não foi atualizado"
        print("  ✓ Campo SKU corrigido atualizado com sucesso!")
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")
    exit(1)

# Testar deletar item (soft delete)
print(f"\n=== Deletando item (soft delete) ===")
req = urllib.request.Request(
    f'http://localhost:8000/api/estoque/itens/{item_id}',
    headers=headers,
    method='DELETE'
)
try:
    with urllib.request.urlopen(req) as response:
        print(f"  ✓ Item deletado (soft delete)")
except urllib.error.HTTPError as e:
    print(f"  ✗ Erro: {e.code}")
    print(f"  Detalhes: {e.read().decode()}")

print("\n=== Testes concluídos com sucesso ===")
