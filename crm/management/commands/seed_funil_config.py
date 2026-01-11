"""
Comando para popular configurações iniciais do funil.
"""

from django.core.management.base import BaseCommand
from crm.models_config import FunilResultadoConfig, FunilProximoPassoConfig


class Command(BaseCommand):
    help = 'Popula configurações iniciais do funil'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Populando configurações iniciais...'))
        
        # ============================================================
        # CLIENTE NOVO - CONTA PARA CONTATO
        # ============================================================
        novo_config = [
            ('contato_responsavel', 'Falou com responsável', 1),
            ('responsavel_indisponivel', 'Responsável não disponível', 2),
            ('nao_atendeu', 'Não atendeu após tentativas', 3),
            ('numero_invalido', 'Número inválido', 4),
        ]
        
        for key, label, ordem in novo_config:
            obj, created = FunilResultadoConfig.objects.get_or_create(
                coluna_pipeline='conta_para_contato',
                status_cliente='novo',
                key=key,
                defaults={
                    'label': label,
                    'ordem': ordem,
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Criado: {obj}')
            else:
                self.stdout.write(f'  - Existe: {obj}')
        
        # Próximo passo para NOVO
        step, created = FunilProximoPassoConfig.objects.get_or_create(
            coluna_pipeline='conta_para_contato',
            status_cliente='novo',
            label='Tentar contato novamente',
            defaults={
                'ordem': 1,
                'ativo': True
            }
        )
        if created:
            self.stdout.write(f'  ✓ Criado próximo passo: {step}')
        
        # ============================================================
        # CLIENTE ATIVO - CONTA PARA CONTATO
        # ============================================================
        ativo_config = [
            ('contato_responsavel', 'Falou com responsável', 1),
            ('em_negociacao', 'Em negociação', 2),
            ('aceitou', 'Pedido realizado', 3),
            ('aguardando_resposta', 'Sem demanda no momento', 4),
        ]
        
        for key, label, ordem in ativo_config:
            obj, created = FunilResultadoConfig.objects.get_or_create(
                coluna_pipeline='conta_para_contato',
                status_cliente='ativo',
                key=key,
                defaults={
                    'label': label,
                    'ordem': ordem,
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Criado: {obj}')
        
        # Próximo passo para ATIVO
        step, created = FunilProximoPassoConfig.objects.get_or_create(
            coluna_pipeline='conta_para_contato',
            status_cliente='ativo',
            label='Tentar contato novamente',
            defaults={
                'ordem': 1,
                'ativo': True
            }
        )
        if created:
            self.stdout.write(f'  ✓ Criado próximo passo: {step}')
        
        # ============================================================
        # CLIENTE INATIVO - CONTA PARA CONTATO
        # ============================================================
        inativo_config = [
            ('contato_responsavel', 'Falou com responsável', 1),
            ('sem_interesse', 'Sem interesse no momento', 2),
            ('sem_perfil', 'Empresa encerrou atividades', 3),
            ('numero_invalido', 'Número inválido', 4),
        ]
        
        for key, label, ordem in inativo_config:
            obj, created = FunilResultadoConfig.objects.get_or_create(
                coluna_pipeline='conta_para_contato',
                status_cliente='inativo',
                key=key,
                defaults={
                    'label': label,
                    'ordem': ordem,
                    'ativo': True
                }
            )
            if created:
                self.stdout.write(f'  ✓ Criado: {obj}')
        
        # Próximo passo para INATIVO
        step, created = FunilProximoPassoConfig.objects.get_or_create(
            coluna_pipeline='conta_para_contato',
            status_cliente='inativo',
            label='Tentar contato novamente',
            defaults={
                'ordem': 1,
                'ativo': True
            }
        )
        if created:
            self.stdout.write(f'  ✓ Criado próximo passo: {step}')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Configurações iniciais populadas!'))
