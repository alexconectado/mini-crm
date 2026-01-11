"""
Comando Django para limpar todos os leads antes de entrar em produção.
Uso: python manage.py limpar_leads
"""

from django.core.management.base import BaseCommand
from crm.models import RegistroComercial, ContatoHistorico


class Command(BaseCommand):
    help = 'Limpa todos os registros comerciais e históricos de contato (PRÉ-PRODUÇÃO)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a limpeza sem confirmação (use com cuidado!)',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.WARNING("LIMPEZA DE DADOS DO CRM - PRÉ-PRODUÇÃO"))
        self.stdout.write("=" * 60)
        self.stdout.write("")
        
        # Contar registros antes
        total_registros = RegistroComercial.objects.count()
        total_contatos = ContatoHistorico.objects.count()
        
        self.stdout.write(f"📊 Registros comerciais encontrados: {total_registros}")
        self.stdout.write(f"📊 Históricos de contato encontrados: {total_contatos}")
        self.stdout.write("")
        
        if total_registros == 0 and total_contatos == 0:
            self.stdout.write(self.style.SUCCESS("✅ Não há dados para limpar!"))
            return
        
        # Confirmação
        if not force:
            self.stdout.write(self.style.ERROR("⚠️  ATENÇÃO: Esta ação NÃO pode ser desfeita!"))
            self.stdout.write(self.style.ERROR("⚠️  Todos os leads e históricos serão PERMANENTEMENTE apagados!"))
            self.stdout.write("")
            
            confirm = input("Digite 'sim' para confirmar: ")
            
            if confirm.lower() != 'sim':
                self.stdout.write(self.style.WARNING("❌ Operação cancelada."))
                return
        
        self.stdout.write("")
        self.stdout.write("🗑️  Limpando dados...")
        
        try:
            # Deletar históricos primeiro (devido à foreign key)
            contatos_deletados, _ = ContatoHistorico.objects.all().delete()
            self.stdout.write(f"   ✓ {contatos_deletados} históricos de contato removidos")
            
            # Deletar registros comerciais
            registros_deletados, _ = RegistroComercial.objects.all().delete()
            self.stdout.write(f"   ✓ {registros_deletados} registros comerciais removidos")
            
            self.stdout.write("")
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.SUCCESS("✅ LIMPEZA CONCLUÍDA COM SUCESSO!"))
            self.stdout.write("=" * 60)
            self.stdout.write("")
            self.stdout.write("O banco de dados está pronto para produção.")
            self.stdout.write("Usuários e grupos foram mantidos.")
            
        except Exception as e:
            self.stdout.write("")
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.ERROR("❌ ERRO DURANTE A LIMPEZA!"))
            self.stdout.write("=" * 60)
            self.stdout.write(self.style.ERROR(f"Erro: {str(e)}"))
            raise
