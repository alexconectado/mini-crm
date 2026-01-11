"""
Admin para configuração do funil.
"""

from django.contrib import admin
from .models_config import FunilResultadoConfig, FunilProximoPassoConfig


@admin.register(FunilResultadoConfig)
class FunilResultadoConfigAdmin(admin.ModelAdmin):
    """Admin para configuração de resultados do funil."""
    
    list_display = ('coluna_pipeline', 'status_cliente', 'label', 'key', 'ativo', 'ordem')
    list_filter = ('coluna_pipeline', 'status_cliente', 'ativo')
    search_fields = ('label', 'key')
    ordering = ('coluna_pipeline', 'status_cliente', 'ordem', 'key')
    
    fieldsets = (
        ('Localização', {
            'fields': ('coluna_pipeline', 'status_cliente')
        }),
        ('Configuração', {
            'fields': ('key', 'label', 'ordem', 'ativo')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Previne editar chave se já existe."""
        if obj:
            return ('key', 'coluna_pipeline', 'status_cliente')
        return ()
    
    actions = ['ativar', 'desativar']
    
    @admin.action(description='Ativar selecionados')
    def ativar(self, request, queryset):
        queryset.update(ativo=True)
    
    @admin.action(description='Desativar selecionados')
    def desativar(self, request, queryset):
        queryset.update(ativo=False)


@admin.register(FunilProximoPassoConfig)
class FunilProximoPassoConfigAdmin(admin.ModelAdmin):
    """Admin para configuração de próximos passos do funil."""
    
    list_display = ('coluna_pipeline', 'status_cliente', 'label', 'ativo', 'ordem')
    list_filter = ('coluna_pipeline', 'status_cliente', 'ativo')
    search_fields = ('label',)
    ordering = ('coluna_pipeline', 'status_cliente', 'ordem', 'label')
    
    fieldsets = (
        ('Localização', {
            'fields': ('coluna_pipeline', 'status_cliente')
        }),
        ('Configuração', {
            'fields': ('label', 'ordem', 'ativo')
        }),
    )
    
    actions = ['ativar', 'desativar']
    
    @admin.action(description='Ativar selecionados')
    def ativar(self, request, queryset):
        queryset.update(ativo=True)
    
    @admin.action(description='Desativar selecionados')
    def desativar(self, request, queryset):
        queryset.update(ativo=False)
