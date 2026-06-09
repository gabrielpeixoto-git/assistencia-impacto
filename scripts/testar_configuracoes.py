import requests
import json

# Configurações
BASE_URL = "http://localhost:8000/api"

# Fazer login
login_url = f"{BASE_URL}/auth/login"
login_data = {
    "email": "admin@assistenciaimpacto.com.br",
    "senha": "admin123"
}

try:
    print("=== Teste de API de Configurações ===\n")
    
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
    
    # Buscar configurações
    print("2. Buscando configurações...")
    configuracoes_url = f"{BASE_URL}/configuracoes"
    response = requests.get(configuracoes_url, headers=headers)
    print(f"   Status: {response.status_code}")
    
    if response.status_code != 200:
        print(f"   Erro ao buscar configurações: {response.text}")
        exit(1)
    
    configuracoes = response.json()
    print(f"   Configurações obtidas com sucesso!\n")
    
    print("3. Exibindo configurações:")
    print(f"   Nome da Empresa: {configuracoes['nome_empresa']}")
    print(f"   CNPJ: {configuracoes['cnpj_empresa']}")
    print(f"   Telefone: {configuracoes['telefone_empresa']}")
    print(f"   Email: {configuracoes['email_empresa']}")
    print(f"   Endereço: {configuracoes['endereco_empresa']}")
    print(f"   SMTP Host: {configuracoes['smtp_host']}")
    print(f"   SMTP Porta: {configuracoes['smtp_porta']}")
    print(f"   SMTP Usuário: {configuracoes['smtp_usuario']}")
    print(f"   Email Remetente: {configuracoes['email_remetente']}")
    print(f"   Evolution API URL: {configuracoes['evolution_api_url']}")
    print(f"   WhatsApp Telefone: {configuracoes['whatsapp_telefone']}")
    print(f"   Ambiente: {configuracoes['ambiente']}")
    print(f"   Permitir Registro Público: {configuracoes['permitir_registro_publico']}")
    print(f"   URL Frontend: {configuracoes['url_frontend']}\n")
    
    print("=== Teste Concluído com Sucesso ===")
    print("\nA API de configurações está funcionando corretamente!")
    print("O frontend pode agora consumir este endpoint para exibir as configurações.")
    
except Exception as e:
    print(f"\nErro durante o teste: {e}")
    import traceback
    traceback.print_exc()
