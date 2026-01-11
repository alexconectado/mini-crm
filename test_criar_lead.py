#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from crm import views

factory = RequestFactory()
user = User.objects.get(username='controller')

# Simular POST
request = factory.post('/crm/criar-registro/', {
    'nome_empresa': 'Teste Script',
    'telefone': '11999999999',
    'cidade': 'São Paulo',
    'uf': 'SP',
    'origem': 'indicacao',
    'canal_contato': 'whatsapp'
})
request.user = user

print("\n=== TESTANDO CRIAR REGISTRO ===")
try:
    response = views.criar_registro(request)
    print(f'✅ Response status: {response.status_code}')
    if hasattr(response, 'url'):
        print(f'Redirect para: {response.url}')
except Exception as e:
    print(f'\n❌ ERRO: {e}')
    print(f'Tipo: {type(e).__name__}')
    import traceback
    print("\nTraceback completo:")
    traceback.print_exc()
