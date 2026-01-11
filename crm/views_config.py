"""
Views para interface de configuração do funil.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from .models_config import FunilResultadoConfig, FunilProximoPassoConfig
from .funil_config_utils import invalidar_cache_funil


def admin_required(view_func):
    """Decorator para exigir admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Acesso negado'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def configuracao_funil(request):
    """Página de configuração do funil para admin."""
    
    # Agrupar por coluna
    colunas = {
        'conta_para_contato': 'Conta para Contato',
        'contato_feito': 'Contato Feito',
        'negociacao_cotacao': 'Negociação / Cotação',
        'pedido_realizado': 'Pedido Realizado',
        'conta_ativa': 'Conta Ativa',
    }
    
    status_cliente_choices = {
        'novo': 'Cliente Novo',
        'ativo': 'Cliente Ativo',
        'inativo': 'Cliente Inativo',
    }
    
    config_data = {}
    
    for col_key, col_label in colunas.items():
        config_data[col_key] = {}
        
        for status_key, status_label in status_cliente_choices.items():
            # Resultados
            resultados = FunilResultadoConfig.objects.filter(
                coluna_pipeline=col_key,
                status_cliente=status_key
            ).order_by('ordem', 'label')
            
            # Próximos passos
            passos = FunilProximoPassoConfig.objects.filter(
                coluna_pipeline=col_key,
                status_cliente=status_key
            ).order_by('ordem', 'label')
            
            config_data[col_key][status_key] = {
                'status_label': status_label,
                'resultados': resultados,
                'passos': passos,
                'resultado_count': resultados.count(),
                'passo_count': passos.count(),
                'resultado_ativos': resultados.filter(ativo=True).count(),
                'passo_ativos': passos.filter(ativo=True).count(),
            }
    
    context = {
        'colunas': colunas,
        'status_cliente_choices': status_cliente_choices,
        'config_data': config_data,
    }
    
    return render(request, 'crm/admin/configuracao_funil.html', context)


@login_required
@admin_required
def toggle_resultado_ativo(request, resultado_id):
    """Toggle ativo/inativo de um resultado."""
    if request.method == 'POST':
        try:
            config = FunilResultadoConfig.objects.get(id=resultado_id)
            config.ativo = not config.ativo
            config.save()
            invalidar_cache_funil()
            return JsonResponse({'success': True, 'ativo': config.ativo})
        except FunilResultadoConfig.DoesNotExist:
            return JsonResponse({'error': 'Não encontrado'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@admin_required
def toggle_passo_ativo(request, passo_id):
    """Toggle ativo/inativo de um próximo passo."""
    if request.method == 'POST':
        try:
            config = FunilProximoPassoConfig.objects.get(id=passo_id)
            config.ativo = not config.ativo
            config.save()
            invalidar_cache_funil()
            return JsonResponse({'success': True, 'ativo': config.ativo})
        except FunilProximoPassoConfig.DoesNotExist:
            return JsonResponse({'error': 'Não encontrado'}, status=404)
    return JsonResponse({'error': 'Método não permitido'}, status=405)
