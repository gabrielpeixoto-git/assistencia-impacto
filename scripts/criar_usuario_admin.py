#!/usr/bin/env python3
"""
Script para criar usuário admin padrão no sistema.
Execute este script para criar um usuário administrador.
"""

import requests
import json

# Configurações
API_URL = "http://localhost:8000/api/auth/registrar"

# Dados do usuário admin
USUARIO_ADMIN = {
    "email": "admin@assistenciaimpacto.com.br",
    "senha": "admin123",
    "nome_completo": "Administrador",
    "perfil": "admin"
}

def criar_usuario_admin():
    """Cria usuário admin através da API."""
    try:
        print("Criando usuário admin...")
        print(f"Email: {USUARIO_ADMIN['email']}")
        print(f"Senha: {USUARIO_ADMIN['senha']}")
        print(f"Nome: {USUARIO_ADMIN['nome_completo']}")
        print(f"Perfil: {USUARIO_ADMIN['perfil']}")
        print()
        
        response = requests.post(API_URL, json=USUARIO_ADMIN)
        
        if response.status_code == 201:
            print("✓ Usuário admin criado com sucesso!")
            print(f"  ID: {response.json().get('usuario_id')}")
            print()
            print("Credenciais de acesso:")
            print(f"  Email: {USUARIO_ADMIN['email']}")
            print(f"  Senha: {USUARIO_ADMIN['senha']}")
            print()
            print("Acesse o sistema em: http://localhost")
        else:
            print(f"✗ Erro ao criar usuário: {response.status_code}")
            print(f"  Detalhes: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("✗ Erro: Não foi possível conectar à API.")
        print("  Certifique-se de que o backend está rodando em http://localhost:8000")
    except Exception as e:
        print(f"✗ Erro: {str(e)}")

if __name__ == "__main__":
    criar_usuario_admin()
