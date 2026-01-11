#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Ativar verbosidade do Django
os.environ['DJANGO_DEBUG'] = '1'

django.setup()

from django.test import Client
from django.contrib.auth.models import User
import logging

logging.basicConfig(level=logging.DEBUG)

# Desabilitar CSRF por enquanto
client = Client(enforce_csrf_checks=False)

# Login
user = User.objects.get(username='controller')
client.force_login(user)

print("=" * 60)
print("TEST 1: POST para /crm/criar-registro/")
print("=" * 60)

try:
    response = client.post('/crm/criar-registro/', {
        'nome_empresa': 'Test Company',
        'telefone': '1122334455',
        'cidade': 'São Paulo',
        'uf': 'SP',
        'origem': 'outros',
        'canal_contato': 'whatsapp'
    }, SERVER_NAME='crm.zandomax.com.br')  # Especificar host válido
    
    print(f"Status: {response.status_code}")
    if response.status_code >= 400:
        print(f"Body: {response.content.decode()}")
    else:
        print("✅ Sucesso!")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()


