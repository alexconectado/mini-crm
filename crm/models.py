import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models_config import FunilResultadoConfig, FunilProximoPassoConfig


class OrigemChoices(models.TextChoices):
    """Enum para origem do registro comercial."""
    BASE_WINTHOR = 'base_winthor', 'Base Winthor'
    GOOGLE = 'google', 'Google'
    SITE = 'site', 'Site'
    INSTAGRAM = 'instagram', 'Instagram'
    INDICACAO = 'indicacao', 'Indicação'
    PROSPECCAO_FRIA = 'prospeccao_fria', 'Prospecção Fria'
    WHATSAPP_ATIVO = 'whatsapp_ativo', 'WhatsApp Ativo'
    OUTROS = 'outros', 'Outros'


class StatusPipelineChoices(models.TextChoices):
    """Enum oficial do pipeline Zandomax."""
    CONTA_PARA_CONTATO = 'conta_para_contato', 'Conta para Contato'
    CONTATO_FEITO = 'contato_feito', 'Contato Feito'
    NEGOCIACAO_COTACAO = 'negociacao_cotacao', 'Negociação / Cotação'
    PEDIDO_REALIZADO = 'pedido_realizado', 'Pedido Realizado'
    CONTA_ATIVA = 'conta_ativa', 'Conta Ativa (Recorrência)'
    ARQUIVADA = 'arquivada', 'Arquivada'


class CanalContatoChoices(models.TextChoices):
    """Enum para canal do contato/comunicação."""
    WHATSAPP = 'whatsapp', 'WhatsApp'
    TELEFONE = 'telefone', 'Telefone'
    EMAIL = 'email', 'E-mail'
    INSTAGRAM = 'instagram', 'Instagram'
    PRESENCIAL = 'presencial', 'Presencial'
    OUTROS = 'outros', 'Outros'


class RegistroComercial(models.Model):
    """
    Model principal do Mini-CRM.
    Representa leads e clientes em potencial.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Dados da Empresa
    codigo_winthor = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Código Winthor",
        help_text="Código do cliente no sistema Winthor (apenas após conversão)"
    )
    nome_empresa = models.CharField(
        max_length=200,
        verbose_name="Nome da Empresa"
    )
    telefone = models.CharField(
        max_length=50,
        verbose_name="Telefone"
    )
    cidade = models.CharField(
        max_length=100,
        verbose_name="Cidade"
    )
    uf = models.CharField(
        max_length=2,
        verbose_name="UF"
    )
    
    # Relacionamento
    vendedor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='registros_comerciais',
        verbose_name="Vendedor"
    )
    
    # Origem e Status
    origem = models.CharField(
        max_length=20,
        choices=OrigemChoices.choices,
        verbose_name="Origem",
        help_text="Origem do lead. Não pode ser alterada após criação."
    )
    canal_contato = models.CharField(
        max_length=20,
        choices=CanalContatoChoices.choices,
        default=CanalContatoChoices.WHATSAPP,
        verbose_name="Canal de Contato",
        help_text="Canal preferencial de comunicação com o lead"
    )
    status_pipeline = models.CharField(
        max_length=30,
        choices=StatusPipelineChoices.choices,
        default=StatusPipelineChoices.CONTA_PARA_CONTATO,
        verbose_name="Status no Pipeline"
    )
    
    # Contexto Operacional
    status_cliente = models.CharField(
        max_length=20,
        choices=[
            ('novo', 'Cliente Novo'),
            ('ativo', 'Cliente Ativo'),
            ('inativo', 'Cliente Inativo'),
        ],
        default='novo',
        verbose_name="Status do Cliente",
        help_text="Contexto operacional que altera opções de resultado sem mudar o funil"
    )
    
    # Histórico de Contato
    ultimo_contato = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Último Contato"
    )
    resultado_ultimo_contato = models.TextField(
        blank=True,
        verbose_name="Resultado do Último Contato",
        help_text="Breve descrição do resultado"
    )
    proximo_passo = models.TextField(
        blank=True,
        verbose_name="Próximo Passo",
        help_text="Breve descrição da próxima ação"
    )
    data_retorno = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Retorno",
        help_text="Data agendada para próximo contato (follow-up)"
    )
    
    # Conversão
    data_conversao_cliente = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Data de Conversão",
        help_text="Data em que virou cliente no Winthor"
    )
    
    # Metadata
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em"
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em"
    )
    
    # Flag para indicar se está no Kanban (trabalho ativo)
    no_kanban = models.BooleanField(
        default=False,
        verbose_name="No Kanban",
        help_text="Indica se o registro está ativo no Kanban"
    )
    
    class Meta:
        verbose_name = "Registro Comercial"
        verbose_name_plural = "Registros Comerciais"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['vendedor', 'status_pipeline']),
            models.Index(fields=['vendedor', 'no_kanban']),
            models.Index(fields=['codigo_winthor']),
            models.Index(fields=['status_pipeline', '-atualizado_em']),
            models.Index(fields=['cidade', 'uf']),
            models.Index(fields=['-criado_em']),
        ]
    
    def __str__(self):
        return f"{self.nome_empresa} - {self.get_status_pipeline_display()}"
    
    def registrar_contato(self, resultado, novo_status=None):
        """
        Registra um novo contato.
        
        Args:
            resultado (str): Descrição do resultado do contato
            novo_status (str, optional): Novo status no pipeline
        """
        self.ultimo_contato = timezone.now()
        self.resultado_ultimo_contato = resultado
        
        if novo_status and novo_status in StatusPipelineChoices.values:
            self.status_pipeline = novo_status
        
        self.save()
    
    def mover_para_kanban(self):
        """Move o registro do backlog para o Kanban."""
        self.no_kanban = True
        self.save()
    
    def mover_para_backlog(self):
        """Remove o registro do Kanban, voltando para o backlog."""
        self.no_kanban = False
        self.save()


class ContatoHistorico(models.Model):
    """
    Histórico de todos os contatos realizados.
    Mantém auditoria completa da interação comercial.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    registro = models.ForeignKey(
        RegistroComercial,
        on_delete=models.CASCADE,
        related_name='historico_contatos',
        verbose_name="Registro"
    )
    
    data_contato = models.DateTimeField(
        default=timezone.now,
        verbose_name="Data do Contato"
    )
    
    resultado = models.TextField(
        verbose_name="Resultado",
        help_text="Descrição do resultado do contato"
    )
    
    status_anterior = models.CharField(
        max_length=30,
        choices=StatusPipelineChoices.choices,
        verbose_name="Status Anterior"
    )
    
    status_novo = models.CharField(
        max_length=30,
        choices=StatusPipelineChoices.choices,
        verbose_name="Status Novo"
    )

    checklist_itens = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Checklist marcado",
        help_text="Checklist aplicado no contato (parcial ou completo)"
    )

    canal_contato = models.CharField(
        max_length=20,
        choices=CanalContatoChoices.choices,
        default=CanalContatoChoices.WHATSAPP,
        verbose_name="Canal do Contato"
    )
    
    usuario = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='contatos_realizados',
        verbose_name="Usuário"
    )
    
    class Meta:
        verbose_name = "Histórico de Contato"
        verbose_name_plural = "Históricos de Contatos"
        ordering = ['-data_contato']
        indexes = [
            models.Index(fields=['registro', '-data_contato']),
            models.Index(fields=['usuario', '-data_contato']),
            models.Index(fields=['status_novo']),
        ]
        indexes = [
            models.Index(fields=['registro', '-data_contato']),
        ]
    
    def __str__(self):
        return f"{self.registro.nome_empresa} - {self.data_contato.strftime('%d/%m/%Y %H:%M')}"
