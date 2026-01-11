"""
Regras fechadas do pipeline de vendas.

Define para cada estágio:
- checklist obrigatório
- resultados possíveis (ENUM)
- mapeamento de avanço automático
"""

# Labels humanizados para resultados
RESULT_LABELS = {
    "contato_responsavel": "Falou com responsável (decisor ou setor de compras)",
    "responsavel_indisponivel": "Responsável não disponível — solicitaram retorno",
    "nao_atendeu": "Não atendeu após tentativas",
    "numero_invalido": "Número inválido",
    "interessado": "Interessado",
    "avaliando": "Avaliando",
    "sem_interesse": "Sem interesse",
    "sem_perfil": "Sem perfil",
    "em_negociacao": "Em negociação",
    "aguardando_resposta": "Aguardando resposta",
    "recusou": "Recusou",
    "aceitou": "Aceitou proposta",
    "finalizado": "Finalizado",
    "arquivado_automatico": "Arquivado automaticamente (limite de retornos atingido)",
}

# Labels humanizados para checklist
CHECKLIST_LABELS = {
    "tentativa_contato_realizada": "Tentativa de contato realizada",
    "canal_utilizado": "Canal validado (Telefone/WhatsApp)",
    "resultado_contato": "Resultado do contato registrado",
    "dor_identificada": "Dor/necessidade identificada",
    "interesse_confirmado": "Interesse confirmado",
    "produto_identificado": "Produto/serviço identificado",
    "proposta_enviada": "Proposta/cotação enviada",
    "valor_apresentado": "Valor apresentado",
    "prazo_informado": "Prazo de entrega informado",
    "pedido_confirmado": "Pedido confirmado",
    "dados_completos": "Dados do cliente completos",
    "forma_pagamento_definida": "Forma de pagamento definida",
}

PIPELINE_RULES = {
    "CONTA_PARA_CONTATO": {
        "checklist": [
            "tentativa_contato_realizada",
            "canal_utilizado",
            "resultado_contato",
        ],
        "results": {
            "contato_responsavel": "CONTATO_FEITO",
            "responsavel_indisponivel": "CONTA_PARA_CONTATO",
            "nao_atendeu": "ARQUIVADO",
            "numero_invalido": "ARQUIVADO",
        },
    },
    "CONTATO_FEITO": {
        "checklist": [
            "dor_identificada",
            "interesse_confirmado",
            "produto_identificado",
        ],
        "results": {
            "interessado": "NEGOCIACAO",
            "avaliando": "CONTATO_FEITO",
            "sem_interesse": "ARQUIVADO",
            "sem_perfil": "ARQUIVADO",
        },
    },
    "NEGOCIACAO": {
        "checklist": [
            "proposta_enviada",
            "valor_apresentado",
            "prazo_informado",
        ],
        "results": {
            "em_negociacao": "NEGOCIACAO",
            "aguardando_resposta": "NEGOCIACAO",
            "recusou": "ARQUIVADO",
            "aceitou": "PEDIDO_REALIZADO",
        },
    },
    "PEDIDO_REALIZADO": {
        "checklist": [
            "pedido_confirmado",
            "dados_completos",
            "forma_pagamento_definida",
        ],
        "results": {
            "finalizado": "CONTA_ATIVA",
        },
    },
    "CONTA_ATIVA": {
        "checklist": [],
        "results": {},
    },
}
