"""
Utilitários para carregar configurações do funil.
Usa database-first, fallback para hardcoded.
"""

from django.core.cache import cache
from .models_config import FunilResultadoConfig, FunilProximoPassoConfig


def obter_resultados_config(coluna_pipeline, status_cliente):
    """
    Obtém resultados configurados para uma coluna e status.
    Com fallback para valores hardcoded se não existir config.
    
    Args:
        coluna_pipeline: ex 'conta_para_contato'
        status_cliente: ex 'novo'
    
    Returns:
        List[dict]: [{'key': '...', 'label': '...', 'next_status_label': '...'}]
    """
    from .views import PIPELINE_RULES, PIPELINE_TO_DB_MAP, STATUS_PIPELINE_MAP
    from .models import StatusPipelineChoices
    
    cache_key = f'funil_resultados_{coluna_pipeline}_{status_cliente}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Tentar carregar da config
    try:
        configs = FunilResultadoConfig.objects.filter(
            coluna_pipeline=coluna_pipeline,
            status_cliente=status_cliente,
            ativo=True
        ).order_by('ordem', 'label')
        
        if configs.exists():
            resultados = []
            current_stage_key = STATUS_PIPELINE_MAP.get(coluna_pipeline, coluna_pipeline)
            pipeline_rules = PIPELINE_RULES.get(current_stage_key, {})
            
            for config in configs:
                # Buscar próximo estágio no PIPELINE_RULES (não mudar!)
                next_stage = pipeline_rules.get('results', {}).get(config.key, current_stage_key)
                db_next_stage = PIPELINE_TO_DB_MAP.get(next_stage, coluna_pipeline)
                next_stage_label = dict(StatusPipelineChoices.choices).get(db_next_stage, db_next_stage)
                
                resultados.append({
                    'key': config.key,
                    'label': config.label,
                    'next_status_label': next_stage_label
                })
            
            cache.set(cache_key, resultados, 3600)  # 1 hora
            return resultados
    except Exception as e:
        print(f"Erro ao carregar config: {e}")
    
    # Fallback: usar RESULTADO_POR_STATUS_CLIENTE
    from .pipeline.rules import RESULTADO_POR_STATUS_CLIENTE, RESULT_LABELS
    
    valid_keys = RESULTADO_POR_STATUS_CLIENTE.get(status_cliente, [])
    resultados = []
    current_stage_key = STATUS_PIPELINE_MAP.get(coluna_pipeline, coluna_pipeline)
    pipeline_rules = PIPELINE_RULES.get(current_stage_key, {})
    
    for k in valid_keys:
        next_stage = pipeline_rules.get('results', {}).get(k, current_stage_key)
        db_next_stage = PIPELINE_TO_DB_MAP.get(next_stage, coluna_pipeline)
        next_stage_label = dict(StatusPipelineChoices.choices).get(db_next_stage, db_next_stage)
        
        resultados.append({
            'key': k,
            'label': RESULT_LABELS.get(k, k),
            'next_status_label': next_stage_label
        })
    
    cache.set(cache_key, resultados, 3600)
    return resultados


def obter_proximos_passos_config(coluna_pipeline, status_cliente):
    """
    Obtém próximos passos configurados para uma coluna e status.
    
    Args:
        coluna_pipeline: ex 'conta_para_contato'
        status_cliente: ex 'novo'
    
    Returns:
        List[str]: Labels dos próximos passos
    """
    
    cache_key = f'funil_proximos_passos_{coluna_pipeline}_{status_cliente}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Tentar carregar da config
    try:
        steps = FunilProximoPassoConfig.objects.filter(
            coluna_pipeline=coluna_pipeline,
            status_cliente=status_cliente,
            ativo=True
        ).order_by('ordem', 'label').values_list('label', flat=True)
        
        steps_list = list(steps)
        if steps_list:
            cache.set(cache_key, steps_list, 3600)
            return steps_list
    except Exception as e:
        print(f"Erro ao carregar próximos passos: {e}")
    
    # Fallback: usar STAGE_CONFIG
    from .views import STAGE_CONFIG
    
    stage_config = STAGE_CONFIG.get(coluna_pipeline, {})
    steps_list = stage_config.get('next_steps', [])
    
    cache.set(cache_key, steps_list, 3600)
    return steps_list


def invalidar_cache_funil():
    """Limpa cache de configurações do funil."""
    from django.core.cache import cache
    import re
    
    # Em desenvolvimento, limpar todos funil_*
    pattern = re.compile(r'funil_.*')
    for key in cache.keys('funil_*'):
        cache.delete(key)
