#!/usr/bin/env python3
"""Debug script para verificar estado do Brostech 3D"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from crm.models import RegistroComercial, ContatoHistorico

# Buscar Brostech 3D
brostech = RegistroComercial.objects.filter(nome_empresa='Brostech 3D').first()

if brostech:
    print(f"\n{'='*60}")
    print(f"  BROSTECH 3D - DEBUG")
    print(f"{'='*60}")
    print(f"  ID: {brostech.id}")
    print(f"  Status: {brostech.status_pipeline}")
    print(f"  Próximo Passo: '{brostech.proximo_passo}'")
    print(f"  Data Retorno: {brostech.data_retorno}")
    print(f"  Resultado: {brostech.resultado_ultimo_contato}")
    print(f"  No Kanban: {brostech.no_kanban}")
    
    print(f"\n{'='*60}")
    print(f"  HISTÓRICO (últimos 10)")
    print(f"{'='*60}")
    historico = brostech.historico_contatos.all().order_by('-data_contato')[:10]
    for i, hist in enumerate(historico, 1):
        print(f"  {i}. {hist.data_contato.strftime('%d/%m %H:%M')} | {hist.resultado} | {hist.status_novo}")
    
    print(f"\n{'='*60}")
    print(f"  CONTAGEM DE RETORNOS")
    print(f"{'='*60}")
    retornos = ContatoHistorico.objects.filter(
        registro=brostech,
        resultado='responsavel_indisponivel'
    ).count()
    print(f"  Total de 'responsavel_indisponivel': {retornos}")
    
    print(f"\n{'='*60}\n")
else:
    print("❌ Brostech 3D não encontrado!")
