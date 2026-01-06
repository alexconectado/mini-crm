"""
Constantes imutáveis do pipeline de vendas.

Define os estágios oficiais e status especiais do CRM.
"""

# Estágios do pipeline (ordem fixa)
STAGES = [
    "CONTA_PARA_CONTATO",
    "CONTATO_FEITO",
    "NEGOCIACAO",
    "PEDIDO_REALIZADO",
    "CONTA_ATIVA",
]

# Status especial de arquivamento
ARCHIVED = "ARQUIVADO"
