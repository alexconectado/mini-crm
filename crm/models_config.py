"""
Modelos de configuração do funil.

Estes models NÃO alteram o core do sistema.
Servem apenas como fonte de configuração para a UI.

O motor de avanço (resolve_next_stage) continua usando PIPELINE_RULES.
"""

from django.db import models


class FunilResultadoConfig(models.Model):
    """
    Configuração de resultados do contato por coluna e status do cliente.
    
    Permite admin customizar quais opções aparecem no formulário.
    NÃO muda lógica de avanço (PIPELINE_RULES é quem decide).
    """
    
    COLUNA_CHOICES = [
        ('conta_para_contato', 'Conta para Contato'),
        ('contato_feito', 'Contato Feito'),
        ('negociacao_cotacao', 'Negociação / Cotação'),
        ('pedido_realizado', 'Pedido Realizado'),
        ('conta_ativa', 'Conta Ativa'),
    ]
    
    STATUS_CLIENTE_CHOICES = [
        ('novo', 'Cliente Novo'),
        ('ativo', 'Cliente Ativo'),
        ('inativo', 'Cliente Inativo'),
    ]
    
    coluna_pipeline = models.CharField(
        max_length=50,
        choices=COLUNA_CHOICES,
        verbose_name="Coluna do Funil"
    )
    
    status_cliente = models.CharField(
        max_length=20,
        choices=STATUS_CLIENTE_CHOICES,
        verbose_name="Status do Cliente"
    )
    
    key = models.CharField(
        max_length=50,
        verbose_name="Chave interna (slug)",
        help_text="Ex: 'contato_responsavel', 'numero_invalido'"
    )
    
    label = models.CharField(
        max_length=150,
        verbose_name="Descrição",
        help_text="O que aparece no select do vendedor"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se marcado, aparece no formulário"
    )
    
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="0-9: ordem de exibição no select"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Configuração de Resultado"
        verbose_name_plural = "Configurações de Resultados"
        ordering = ['coluna_pipeline', 'status_cliente', 'ordem', 'key']
        unique_together = [('coluna_pipeline', 'status_cliente', 'key')]
        indexes = [
            models.Index(fields=['coluna_pipeline', 'status_cliente', 'ativo']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.get_coluna_pipeline_display()} / {self.get_status_cliente_display()} → {self.label}"


class FunilProximoPassoConfig(models.Model):
    """
    Configuração de próximos passos por coluna e status do cliente.
    
    NÃO move card. Apenas lista informativa.
    """
    
    COLUNA_CHOICES = [
        ('conta_para_contato', 'Conta para Contato'),
        ('contato_feito', 'Contato Feito'),
        ('negociacao_cotacao', 'Negociação / Cotação'),
        ('pedido_realizado', 'Pedido Realizado'),
        ('conta_ativa', 'Conta Ativa'),
    ]
    
    STATUS_CLIENTE_CHOICES = [
        ('novo', 'Cliente Novo'),
        ('ativo', 'Cliente Ativo'),
        ('inativo', 'Cliente Inativo'),
    ]
    
    coluna_pipeline = models.CharField(
        max_length=50,
        choices=COLUNA_CHOICES,
        verbose_name="Coluna do Funil"
    )
    
    status_cliente = models.CharField(
        max_length=20,
        choices=STATUS_CLIENTE_CHOICES,
        verbose_name="Status do Cliente"
    )
    
    label = models.CharField(
        max_length=150,
        verbose_name="Próximo Passo",
        help_text="Ex: 'Tentar contato novamente'"
    )
    
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Se marcado, aparece no formulário"
    )
    
    ordem = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordem",
        help_text="0-9: ordem de exibição no select"
    )
    
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    class Meta:
        verbose_name = "Configuração de Próximo Passo"
        verbose_name_plural = "Configurações de Próximos Passos"
        ordering = ['coluna_pipeline', 'status_cliente', 'ordem', 'label']
        indexes = [
            models.Index(fields=['coluna_pipeline', 'status_cliente', 'ativo']),
            models.Index(fields=['ativo']),
        ]
    
    def __str__(self):
        return f"{self.get_coluna_pipeline_display()} / {self.get_status_cliente_display()} → {self.label}"
