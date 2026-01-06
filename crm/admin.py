from django.contrib import admin
from django.utils.html import format_html
from .models import RegistroComercial, ContatoHistorico


@admin.register(RegistroComercial)
class RegistroComercialAdmin(admin.ModelAdmin):
    """Admin para Registro Comercial."""
    
    list_display = [
        'nome_empresa',
        'vendedor',
        'origem',
        'status_pipeline_badge',
        'no_kanban_badge',
        'ultimo_contato',
        'cidade',
        'uf'
    ]
    
    list_filter = [
        'status_pipeline',
        'origem',
        'no_kanban',
        'vendedor',
        'uf',
        'criado_em'
    ]
    
    search_fields = [
        'nome_empresa',
        'telefone',
        'codigo_winthor',
        'cidade'
    ]
    
    readonly_fields = [
        'id',
        'criado_em',
        'atualizado_em'
    ]
    
    fieldsets = (
        ('Dados da Empresa', {
            'fields': (
                'nome_empresa',
                'telefone',
                'cidade',
                'uf',
                'codigo_winthor'
            )
        }),
        ('Comercial', {
            'fields': (
                'vendedor',
                'origem',
                'status_pipeline',
                'no_kanban'
            )
        }),
        ('Histórico de Contato', {
            'fields': (
                'ultimo_contato',
                'resultado_ultimo_contato',
                'proximo_passo'
            )
        }),
        ('Conversão', {
            'fields': (
                'data_conversao_cliente',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'id',
                'criado_em',
                'atualizado_em'
            ),
            'classes': ('collapse',)
        })
    )
    
    def status_pipeline_badge(self, obj):
        """Exibe status com badge colorido."""
        colors = {
            'importado': '#6c757d',
            'contatado': '#0dcaf0',
            'conversou': '#0d6efd',
            'interesse': '#ffc107',
            'pedido': '#198754',
            'perdido': '#dc3545'
        }
        color = colors.get(obj.status_pipeline, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_pipeline_display()
        )
    status_pipeline_badge.short_description = 'Status'
    
    def no_kanban_badge(self, obj):
        """Exibe badge indicando se está no Kanban."""
        if obj.no_kanban:
            return format_html(
                '<span style="background-color: #198754; color: white; padding: 3px 8px; '
                'border-radius: 3px; font-size: 11px;">✓ Kanban</span>'
            )
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">Backlog</span>'
        )
    no_kanban_badge.short_description = 'Localização'
    
    def get_readonly_fields(self, request, obj=None):
        """Torna o campo origem read-only após criação."""
        if obj:  # Editando objeto existente
            return self.readonly_fields + ['origem']
        return self.readonly_fields
    
    def get_queryset(self, request):
        """Filtra registros por vendedor se não for superusuário."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(vendedor=request.user)


@admin.register(ContatoHistorico)
class ContatoHistoricoAdmin(admin.ModelAdmin):
    """Admin para Histórico de Contatos."""
    
    list_display = [
        'registro',
        'data_contato',
        'usuario',
        'status_anterior',
        'status_novo',
        'resultado_preview'
    ]
    
    list_filter = [
        'data_contato',
        'usuario',
        'status_anterior',
        'status_novo'
    ]
    
    search_fields = [
        'registro__nome_empresa',
        'resultado'
    ]
    
    readonly_fields = [
        'id',
        'registro',
        'data_contato',
        'usuario',
        'status_anterior',
        'status_novo',
        'resultado'
    ]
    
    def resultado_preview(self, obj):
        """Exibe preview do resultado."""
        if len(obj.resultado) > 50:
            return obj.resultado[:50] + '...'
        return obj.resultado
    resultado_preview.short_description = 'Resultado'
    
    def has_add_permission(self, request):
        """Desabilita criação manual no admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Desabilita edição no admin."""
        return False
    
    def get_queryset(self, request):
        """Filtra histórico por vendedor se não for superusuário."""
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(usuario=request.user)
