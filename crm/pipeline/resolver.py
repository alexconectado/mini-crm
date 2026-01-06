"""
Motor do pipeline: resolve próximo estágio automaticamente.

Funções puras em Python, sem dependências do Django.
"""

from .rules import PIPELINE_RULES
from .constants import ARCHIVED


def checklist_completo(stage: str, checklist: dict) -> bool:
    """
    Retorna True apenas se TODOS os itens obrigatórios do estágio
    estiverem presentes e com valor True.

    Args:
        stage: Estágio atual (ex: "CONTA_PARA_CONTATO")
        checklist: Dicionário com itens marcados (ex: {"item1": True, "item2": False})

    Returns:
        bool: True se checklist completo, False caso contrário

    Examples:
        >>> checklist_completo("CONTA_PARA_CONTATO", {"tentativa_contato_realizada": True})
        False
        >>> checklist_completo("CONTA_PARA_CONTATO", {
        ...     "tentativa_contato_realizada": True,
        ...     "canal_utilizado": True,
        ...     "resultado_contato": True
        ... })
        True
    """
    if stage not in PIPELINE_RULES:
        return False

    required_items = PIPELINE_RULES[stage].get("checklist", [])

    # Se não há checklist obrigatório, considera completo
    if not required_items:
        return True

    # Verifica se TODOS os itens obrigatórios estão presentes e True
    for item in required_items:
        if not checklist.get(item, False):
            return False

    return True


def resolve_next_stage(stage: str, result: str, checklist: dict) -> str:
    """
    Decide automaticamente o próximo estágio com base em:
    - estágio atual
    - resultado (ENUM)
    - checklist

    Regras:
    - Se checklist incompleto → levanta ValueError
    - Se resultado inválido → ValueError
    - Se regra levar a ARQUIVADO → retorna "ARQUIVADO"
    - Caso contrário → retorna próximo estágio

    Args:
        stage: Estágio atual (ex: "CONTA_PARA_CONTATO")
        result: Resultado do contato (ex: "falou_com_decisor")
        checklist: Dicionário com itens marcados

    Returns:
        str: Próximo estágio ou "ARQUIVADO"

    Raises:
        ValueError: Se estágio inválido, resultado inválido, ou checklist incompleto

    Examples:
        >>> checklist = {
        ...     "tentativa_contato_realizada": True,
        ...     "canal_utilizado": True,
        ...     "resultado_contato": True
        ... }
        >>> resolve_next_stage("CONTA_PARA_CONTATO", "falou_com_decisor", checklist)
        'CONTATO_FEITO'
        >>> resolve_next_stage("CONTA_PARA_CONTATO", "numero_invalido", checklist)
        'ARQUIVADO'
    """
    # Validar estágio
    if stage not in PIPELINE_RULES:
        raise ValueError(f"Estágio inválido: {stage}")

    stage_rules = PIPELINE_RULES[stage]

    # Validar resultado
    if result not in stage_rules.get("results", {}):
        raise ValueError(
            f"Resultado '{result}' inválido para estágio '{stage}'. "
            f"Resultados válidos: {list(stage_rules.get('results', {}).keys())}"
        )

    # Validar checklist (somente para avanços, não para permanecer ou arquivar)
    next_stage = stage_rules["results"][result]
    
    # Se vai avançar (mudar de estágio para frente), exige checklist completo
    if next_stage != stage and next_stage != ARCHIVED:
        if not checklist_completo(stage, checklist):
            raise ValueError(
                f"Checklist incompleto para avançar de '{stage}'. "
                f"Itens obrigatórios: {stage_rules.get('checklist', [])}"
            )

    return next_stage


# ========== TESTES MANUAIS ==========
if __name__ == "__main__":
    print("=" * 60)
    print("TESTES DO MOTOR DE PIPELINE")
    print("=" * 60)

    # Teste 1: Checklist completo
    print("\n[TESTE 1] Checklist completo:")
    checklist_completo_test = {
        "tentativa_contato_realizada": True,
        "canal_utilizado": True,
        "resultado_contato": True,
    }
    resultado = checklist_completo("CONTA_PARA_CONTATO", checklist_completo_test)
    print(f"  Checklist completo? {resultado}")
    assert resultado is True, "Deveria ser True"
    print("  ✅ PASSOU")

    # Teste 2: Checklist incompleto
    print("\n[TESTE 2] Checklist incompleto:")
    checklist_incompleto = {
        "tentativa_contato_realizada": True,
        "canal_utilizado": False,
    }
    resultado = checklist_completo("CONTA_PARA_CONTATO", checklist_incompleto)
    print(f"  Checklist completo? {resultado}")
    assert resultado is False, "Deveria ser False"
    print("  ✅ PASSOU")

    # Teste 3: Avanço com checklist completo
    print("\n[TESTE 3] Avanço com checklist completo:")
    next_stage = resolve_next_stage(
        "CONTA_PARA_CONTATO", "falou_com_decisor", checklist_completo_test
    )
    print(f"  CONTA_PARA_CONTATO + falou_com_decisor → {next_stage}")
    assert next_stage == "CONTATO_FEITO", "Deveria avançar para CONTATO_FEITO"
    print("  ✅ PASSOU")

    # Teste 4: Arquivamento automático
    print("\n[TESTE 4] Arquivamento automático:")
    next_stage = resolve_next_stage(
        "CONTA_PARA_CONTATO", "numero_invalido", checklist_completo_test
    )
    print(f"  CONTA_PARA_CONTATO + numero_invalido → {next_stage}")
    assert next_stage == "ARQUIVADO", "Deveria arquivar"
    print("  ✅ PASSOU")

    # Teste 5: Permanecer no estágio
    print("\n[TESTE 5] Permanecer no estágio:")
    next_stage = resolve_next_stage(
        "CONTA_PARA_CONTATO", "nao_atendeu", checklist_incompleto
    )
    print(f"  CONTA_PARA_CONTATO + nao_atendeu → {next_stage}")
    assert next_stage == "CONTA_PARA_CONTATO", "Deveria permanecer"
    print("  ✅ PASSOU")

    # Teste 6: Erro ao avançar sem checklist completo
    print("\n[TESTE 6] Erro ao avançar sem checklist completo:")
    try:
        resolve_next_stage(
            "CONTA_PARA_CONTATO", "falou_com_decisor", checklist_incompleto
        )
        print("  ❌ FALHOU - deveria ter levantado ValueError")
    except ValueError as e:
        print(f"  ValueError esperado: {e}")
        print("  ✅ PASSOU")

    # Teste 7: Erro com resultado inválido
    print("\n[TESTE 7] Erro com resultado inválido:")
    try:
        resolve_next_stage(
            "CONTA_PARA_CONTATO", "resultado_inexistente", checklist_completo_test
        )
        print("  ❌ FALHOU - deveria ter levantado ValueError")
    except ValueError as e:
        print(f"  ValueError esperado: {e}")
        print("  ✅ PASSOU")

    # Teste 8: Pipeline completo (CONTATO_FEITO → NEGOCIACAO)
    print("\n[TESTE 8] Pipeline completo (CONTATO_FEITO → NEGOCIACAO):")
    checklist_contato = {
        "dor_identificada": True,
        "interesse_confirmado": True,
        "produto_identificado": True,
    }
    next_stage = resolve_next_stage("CONTATO_FEITO", "interessado", checklist_contato)
    print(f"  CONTATO_FEITO + interessado → {next_stage}")
    assert next_stage == "NEGOCIACAO", "Deveria avançar para NEGOCIACAO"
    print("  ✅ PASSOU")

    print("\n" + "=" * 60)
    print("TODOS OS TESTES PASSARAM! ✅")
    print("=" * 60)
