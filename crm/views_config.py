"""
Views para interface de configuração do funil.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.db import models
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
    
    # Agrupar por coluna (4 etapas)
    colunas = {
        'lead': 'Lead',
        'conta_para_contato': 'Conta para Contato',
        'negociacao_cotacao': 'Negociação / Cotação',
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
def criar_resultado(request):
    """API para criar novo resultado."""
    if request.method == 'POST':
        try:
            coluna = request.POST.get('coluna_pipeline')
            status = request.POST.get('status_cliente')
            key = request.POST.get('key')
            label = request.POST.get('label')
            next_status = request.POST.get('next_status', '')
            
            if not all([coluna, status, key, label]):
                return JsonResponse({'error': 'Campos obrigatórios faltando'}, status=400)
            
            # Verificar se já existe
            if FunilResultadoConfig.objects.filter(coluna_pipeline=coluna, status_cliente=status, key=key).exists():
                return JsonResponse({'error': 'Já existe resultado com essa chave'}, status=400)
            
            # Obter próxima ordem
            max_ordem = FunilResultadoConfig.objects.filter(
                coluna_pipeline=coluna, status_cliente=status
            ).aggregate(models.Max('ordem'))['ordem__max'] or 0
            
            resultado = FunilResultadoConfig.objects.create(
                coluna_pipeline=coluna,
                status_cliente=status,
                key=key,
                label=label,
                next_status_label=next_status,
                ordem=max_ordem + 1,
                ativo=True
            )
            
            invalidar_cache_funil()
            
            return JsonResponse({
                'success': True,
                'id': resultado.id,
                'message': 'Resultado criado com sucesso'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@admin_required
def editar_resultado(request, resultado_id):
    """API para editar resultado existente."""
    if request.method == 'POST':
        try:
            resultado = FunilResultadoConfig.objects.get(id=resultado_id)
            
            key = request.POST.get('key')
            label = request.POST.get('label')
            next_status = request.POST.get('next_status', '')
            
            if key:
                # Verificar duplicata (exceto o próprio)
                if FunilResultadoConfig.objects.filter(
                    coluna_pipeline=resultado.coluna_pipeline,
                    status_cliente=resultado.status_cliente,
                    key=key
                ).exclude(id=resultado_id).exists():
                    return JsonResponse({'error': 'Já existe resultado com essa chave'}, status=400)
                resultado.key = key
            
            if label:
                resultado.label = label
            
            resultado.next_status_label = next_status
            resultado.save()
            
            invalidar_cache_funil()
            
            return JsonResponse({
                'success': True,
                'message': 'Resultado atualizado com sucesso'
            })
        except FunilResultadoConfig.DoesNotExist:
            return JsonResponse({'error': 'Resultado não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@admin_required
def excluir_resultado(request, resultado_id):
    """API para excluir resultado."""
    if request.method == 'POST':
        try:
            resultado = FunilResultadoConfig.objects.get(id=resultado_id)
            resultado.delete()
            
            invalidar_cache_funil()
            
            return JsonResponse({
                'success': True,
                'message': 'Resultado excluído com sucesso'
            })
        except FunilResultadoConfig.DoesNotExist:
            return JsonResponse({'error': 'Resultado não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@admin_required
def criar_passo(request):
    """API para criar novo próximo passo."""
    if request.method == 'POST':
        try:
            coluna = request.POST.get('coluna_pipeline')
            status = request.POST.get('status_cliente')
            label = request.POST.get('label')
            
            if not all([coluna, status, label]):
                return JsonResponse({'error': 'Campos obrigatórios faltando'}, status=400)
            
            # Obter próxima ordem
            max_ordem = FunilProximoPassoConfig.objects.filter(
                coluna_pipeline=coluna, status_cliente=status
            ).aggregate(models.Max('ordem'))['ordem__max'] or 0
            
            passo = FunilProximoPassoConfig.objects.create(
                coluna_pipeline=coluna,
                status_cliente=status,
                label=label,
                ordem=max_ordem + 1,
                ativo=True
            )
            
            invalidar_cache_funil()
            
            return JsonResponse({
                'success': True,
                'id': passo.id,
                'message': 'Próximo passo criado com sucesso'
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@admin_required
def editar_passo(request, passo_id):
    """API para editar próximo passo existente."""
    if request.method == 'POST':
        try:
            passo = FunilProximoPassoConfig.objects.get(id=passo_id)
            
            label = request.POST.get('label')
            if label:
                passo.label = label
                passo.save()
            
            invalidar_cache_funil()
            
            return JsonResponse({
                'success': True,
                'message': 'Próximo passo atualizado com sucesso'
            })
        except FunilProximoPassoConfig.DoesNotExist:
            return JsonResponse({'error': 'Próximo passo não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@admin_required
def excluir_passo(request, passo_id):
    """API para excluir próximo passo."""
    if request.method == 'POST':
        try:
            passo = FunilProximoPassoConfig.objects.get(id=passo_id)
            passo.delete()
            
            invalidar_cache_funil()
            
            return JsonResponse({
                'success': True,
                'message': 'Próximo passo excluído com sucesso'
            })
        except FunilProximoPassoConfig.DoesNotExist:
            return JsonResponse({'error': 'Próximo passo não encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


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
