import requests
import json
from datetime import datetime, timedelta

# Configurações
BASE_URL = "http://localhost:8000/api"

# Fazer login
login_url = f"{BASE_URL}/auth/login"
login_data = {
    "email": "admin@assistenciaimpacto.com.br",
    "senha": "admin123"
}

try:
    print("=== Teste de Envio de Orçamento com Notificações ===\n")
    
    # Login
    print("1. Fazendo login...")
    response = requests.post(login_url, json=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Erro no login: {response.text}")
        exit(1)
    
    token = response.json().get("access_token")
    print(f"   Token obtido: {token[:20]}...\n")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Buscar clientes
    print("2. Buscando clientes...")
    clientes_url = f"{BASE_URL}/clientes?ativo=true&limit=10"
    response = requests.get(clientes_url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Erro ao buscar clientes: {response.text}")
        exit(1)
    
    clientes = response.json()
    print(f"   Clientes encontrados: {len(clientes)}")
    
    # Buscar cliente com email e whatsapp
    cliente_teste = None
    for cliente in clientes:
        if cliente.get('email') and cliente.get('whatsapp'):
            cliente_teste = cliente
            break
    
    if not cliente_teste:
        print("   Nenhum cliente com email e whatsapp encontrado. Usando primeiro cliente disponível.")
        cliente_teste = clientes[0] if clientes else None
    
    if not cliente_teste:
        print("   Nenhum cliente encontrado. Criando cliente de teste...")
        cliente_data = {
            "nome": "Cliente Teste Notificações",
            "email": "cliente@teste.com",
            "whatsapp": "5511999999999",
            "telefone": "5511999999999",
            "tipo_documento": "cpf",
            "numero_documento": "12345678901",
            "tipo_cliente": "residencial",
            "logradouro": "Rua Teste",
            "numero": "123",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01310100"
        }
        response = requests.post(clientes_url, json=cliente_data, headers=headers)
        if response.status_code == 201:
            cliente_teste = response.json()
            print(f"   Cliente criado: {cliente_teste['nome']} (ID: {cliente_teste['id']})")
        else:
            print(f"   Erro ao criar cliente: {response.text}")
            exit(1)
    
    print(f"   Cliente selecionado: {cliente_teste['nome']}")
    print(f"   Email: {cliente_teste.get('email', 'N/A')}")
    print(f"   WhatsApp: {cliente_teste.get('whatsapp', 'N/A')}\n")
    
    # Criar orçamento
    print("3. Criando orçamento...")
    orcamento_data = {
        "cliente_id": cliente_teste['id'],
        "titulo": "Orçamento Teste de Notificações",
        "descricao": "Este é um orçamento para testar o envio de notificações por email e WhatsApp.",
        "valido_ate": (datetime.now() + timedelta(days=30)).isoformat(),
        "condicoes_pagamento": "50% na entrega, 50% após 30 dias",
        "garantia": "90 dias",
        "tipo_desconto": "percentual",
        "valor_desconto": 10,
        "taxa_imposto": 0,
        "observacoes_internas": "Teste de envio de notificações"
    }
    
    orcamento_url = f"{BASE_URL}/orcamentos"
    response = requests.post(orcamento_url, json=orcamento_data, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"   Erro ao criar orçamento: {response.text}")
        exit(1)
    
    orcamento = response.json()
    print(f"   Orçamento criado: {orcamento['numero_orcamento']} (ID: {orcamento['id']})")
    print(f"   Status: {orcamento['status']}\n")
    
    # Enviar orçamento
    print("4. Enviando orçamento (disparará notificações)...")
    enviar_url = f"{BASE_URL}/orcamentos/{orcamento['id']}/enviar"
    response = requests.post(enviar_url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Erro ao enviar orçamento: {response.text}")
        exit(1)
    
    resultado = response.json()
    print(f"   Mensagem: {resultado['mensagem']}\n")
    
    # Verificar status atualizado
    print("5. Verificando status atualizado...")
    response = requests.get(f"{BASE_URL}/orcamentos/{orcamento['id']}", headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        orcamento_atualizado = response.json()
        print(f"   Status do orçamento: {orcamento_atualizado['status']}")
        print(f"   Enviado em: {orcamento_atualizado.get('enviado_em', 'N/A')}\n")
    
    print("=== Teste Concluído com Sucesso ===")
    print("\nNotas:")
    print("- Email deve ter sido enviado para: " + cliente_teste.get('email', 'N/A'))
    print("- WhatsApp deve ter sido enviado para: " + cliente_teste.get('whatsapp', 'N/A'))
    print("- Verifique os logs do backend para confirmar o envio das notificações")
    
except Exception as e:
    print(f"\nErro durante o teste: {e}")
    import traceback
    traceback.print_exc()
