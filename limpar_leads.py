#!/usr/bin/env python
"""
Script para limpar todos os leads do banco de dados antes de entrar em produção.
ATENÇÃO: Este script irá apagar TODOS os registros comerciais e históricos de contato!
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import RegistroComercial, ContatoHistorico
from django.contrib.auth.models import User

def limpar_dados():
    """Limpa todos os dados de teste do CRM."""
    
    print("=" * 60)
    print("LIMPEZA DE DADOS DO CRM - PRÉ-PRODUÇÃO")
    print("=" * 60)
    print()
    
    # Contar registros antes
    total_registros = RegistroComercial.objects.count()
    total_contatos = ContatoHistorico.objects.count()
    
    print(f"📊 Registros comerciais encontrados: {total_registros}")
    print(f"📊 Históricos de contato encontrados: {total_contatos}")
    print()
    
    if total_registros == 0 and total_contatos == 0:
        print("✅ Não há dados para limpar!")
        return
    
    # Confirmação
    print("⚠️  ATENÇÃO: Esta ação NÃO pode ser desfeita!")
    print("⚠️  Todos os leads e históricos serão PERMANENTEMENTE apagados!")
    print()
    
    resposta = input("Digite 'CONFIRMAR' para prosseguir com a limpeza: ")
    
    if resposta != "CONFIRMAR":
        print("❌ Operação cancelada.")
        return
    
    print()
    print("🗑️  Limpando dados...")
    
    try:
        # Deletar históricos primeiro (devido à foreign key)
        contatos_deletados = ContatoHistorico.objects.all().delete()
        print(f"   ✓ {contatos_deletados[0]} históricos de contato removidos")
        
        # Deletar registros comerciais
        registros_deletados = RegistroComercial.objects.all().delete()
        print(f"   ✓ {registros_deletados[0]} registros comerciais removidos")
        
        print()
        print("=" * 60)
        print("✅ LIMPEZA CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print()
        print("O banco de dados está pronto para produção.")
        print("Usuários e grupos foram mantidos.")
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRO DURANTE A LIMPEZA!")
        print("=" * 60)
        print(f"Erro: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    limpar_dados()
