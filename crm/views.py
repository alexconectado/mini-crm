from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.db.models import Count, Q
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from .models import (
    RegistroComercial,
    ContatoHistorico,
    StatusPipelineChoices,
    OrigemChoices,
    CanalContatoChoices,
)
from .decorators import comercial_required, admin_required, api_login_required, api_comercial_required
import csv
import json

# Pipeline module (event-driven, automatic transitions)
from crm.pipeline import resolve_next_stage, checklist_completo
from crm.pipeline.rules import PIPELINE_RULES, RESULT_LABELS, CHECKLIST_LABELS, RESULTADO_POR_STATUS_CLIENTE


# Mapeamento de status: banco → chaves de PIPELINE_RULES (tradutor canônico)
STATUS_PIPELINE_MAP = {
    'conta_para_contato': 'CONTA_PARA_CONTATO',
    'contato_feito': 'CONTATO_FEITO',
    'negociacao_cotacao': 'NEGOCIACAO',
    'pedido_realizado': 'PEDIDO_REALIZADO',
    'conta_ativa': 'CONTA_ATIVA',
}

# Mapeamento inverso: chaves do pipeline → valores do banco
PIPELINE_TO_DB_MAP = {
    'CONTA_PARA_CONTATO': StatusPipelineChoices.CONTA_PARA_CONTATO.value,
    'CONTATO_FEITO': StatusPipelineChoices.CONTATO_FEITO.value,
    'NEGOCIACAO': StatusPipelineChoices.NEGOCIACAO_COTACAO.value,
    'PEDIDO_REALIZADO': StatusPipelineChoices.PEDIDO_REALIZADO.value,
    'CONTA_ATIVA': StatusPipelineChoices.CONTA_ATIVA.value,
    'ARQUIVADO': StatusPipelineChoices.ARQUIVADA.value,
}


# Ordem e configuração oficial do pipeline
PIPELINE_SEQUENCE = [
    (StatusPipelineChoices.CONTA_PARA_CONTATO, StatusPipelineChoices.CONTA_PARA_CONTATO.label),
    (StatusPipelineChoices.CONTATO_FEITO, StatusPipelineChoices.CONTATO_FEITO.label),
    (StatusPipelineChoices.NEGOCIACAO_COTACAO, StatusPipelineChoices.NEGOCIACAO_COTACAO.label),
    (StatusPipelineChoices.PEDIDO_REALIZADO, StatusPipelineChoices.PEDIDO_REALIZADO.label),
    (StatusPipelineChoices.CONTA_ATIVA, StatusPipelineChoices.CONTA_ATIVA.label),
    (StatusPipelineChoices.ARQUIVADA, StatusPipelineChoices.ARQUIVADA.label),
]

# Kanban exibe apenas estágios operacionais (exclui Arquivada e Conta Ativa)
KANBAN_STATUSES = [
    (StatusPipelineChoices.CONTA_PARA_CONTATO.value, StatusPipelineChoices.CONTA_PARA_CONTATO.label),
    (StatusPipelineChoices.CONTATO_FEITO.value, StatusPipelineChoices.CONTATO_FEITO.label),
    (StatusPipelineChoices.NEGOCIACAO_COTACAO.value, StatusPipelineChoices.NEGOCIACAO_COTACAO.label),
    (StatusPipelineChoices.PEDIDO_REALIZADO.value, StatusPipelineChoices.PEDIDO_REALIZADO.label),
]

STAGE_CONFIG = {
    StatusPipelineChoices.CONTA_PARA_CONTATO.value: {
        'checklist': [
            'Tentativa de contato realizada',
            'Canal validado (Telefone / WhatsApp)',
            'Decisor identificado',
        ],
        'next_steps': [
            'Tentar contato',
            'Validar canal',
            'Identificar decisor',
            'Retornar contato (data combinada)',
        ],
        'allowed_to': [
            StatusPipelineChoices.CONTATO_FEITO.value,
            StatusPipelineChoices.ARQUIVADA.value,
        ],
        'require_contact': True,
        'require_next_step': True,
        'require_checklist': False,
    },
    StatusPipelineChoices.CONTATO_FEITO.value: {
        'checklist': [
            'Lista de preços enviada',
            'Cotação solicitada',
            'Retorno agendado',
            'Encaminhado para decisor',
        ],
        'next_steps': [
            'Enviar lista de preços',
            'Solicitar mix de produtos',
            'Agendar retorno',
            'Falar com decisor',
        ],
        'allowed_to': [
            StatusPipelineChoices.NEGOCIACAO_COTACAO.value,
            StatusPipelineChoices.CONTA_PARA_CONTATO.value,
            StatusPipelineChoices.ARQUIVADA.value,
        ],
        'require_contact': True,
        'require_next_step': True,
        'require_checklist': True,
    },
    StatusPipelineChoices.NEGOCIACAO_COTACAO.value: {
        'checklist': [
            'Cotação enviada',
            'Follow-up realizado',
            'Ajuste de condição',
            'Pedido confirmado',
        ],
        'next_steps': [
            'Follow-up cotação',
            'Ajustar condição',
            'Confirmar pedido',
        ],
        'allowed_to': [
            StatusPipelineChoices.PEDIDO_REALIZADO.value,
            StatusPipelineChoices.CONTATO_FEITO.value,
            StatusPipelineChoices.ARQUIVADA.value,
        ],
        'require_contact': True,
        'require_next_step': True,
        'require_checklist': True,
    },
    StatusPipelineChoices.PEDIDO_REALIZADO.value: {
        'checklist': [
            'Pedido registrado no ERP (Winthor)',
            'Entrega confirmada',
            'Pós-venda agendado',
        ],
        'next_steps': [
            'Confirmar entrega',
            'Realizar pós-venda',
            'Programar recompra',
        ],
        'allowed_to': [
            StatusPipelineChoices.CONTA_ATIVA.value,
        ],
        'require_contact': True,
        'require_next_step': True,
        'require_checklist': True,
    },
    StatusPipelineChoices.CONTA_ATIVA.value: {
        'checklist': [
            'Follow-up periódico',
            'Reposição de estoque',
            'Oferta de novos produtos',
        ],
        'next_steps': [
            'Reposição',
            'Upsell / cross-sell',
            'Novo pedido',
        ],
        'allowed_to': [
            StatusPipelineChoices.NEGOCIACAO_COTACAO.value,
            StatusPipelineChoices.CONTA_PARA_CONTATO.value,
            StatusPipelineChoices.ARQUIVADA.value,
        ],
        'require_contact': True,
        'require_next_step': True,
        'require_checklist': False,
    },
    StatusPipelineChoices.ARQUIVADA.value: {
        'checklist': [],
        'next_steps': [],
        'allowed_to': [
            StatusPipelineChoices.CONTA_PARA_CONTATO.value,
        ],
        'require_contact': False,
        'require_next_step': False,
        'require_checklist': False,
    },
}


def allowed_transitions(status_key: str):
    return STAGE_CONFIG.get(status_key, {}).get('allowed_to', [])


@comercial_required
def kanban_view(request):
    """View principal do Kanban."""
    user = request.user
    
    # Filtrar registros por vendedor (a menos que seja gestor)
    vendedor_filter = request.GET.get('vendedor')
    if user.is_superuser:
        if vendedor_filter and vendedor_filter != 'todos':
            all_registros = RegistroComercial.objects.filter(vendedor_id=vendedor_filter)
        else:
            all_registros = RegistroComercial.objects.all()
    else:
        all_registros = RegistroComercial.objects.filter(vendedor=user)
        vendedor_filter = None  # Vendedores não têm acesso ao filtro
    
    # Backlog: apenas primeiros 10 registros (paginado depois)
    backlog = all_registros.filter(no_kanban=False).order_by('-criado_em')[:10]
    backlog_count = all_registros.filter(no_kanban=False).count()
    
    # Kanban: registros ativos (exclui Arquivado e Conta Ativa) - primeiros 8 por status
    kanban_all = all_registros.filter(no_kanban=True).exclude(
        status_pipeline__in=[
            StatusPipelineChoices.ARQUIVADA.value,
            StatusPipelineChoices.CONTA_ATIVA.value,
        ]
    ).order_by('status_pipeline', '-atualizado_em')
    
    # Paginação por status: 8 itens por status inicial
    kanban_by_status = {}
    kanban_counts = {}
    for status_key, _ in KANBAN_STATUSES:
        registros_status = all_registros.filter(
            no_kanban=True,
            status_pipeline=status_key
        )
        
        # Ordenação especial para "Conta para Contato"
        if status_key == StatusPipelineChoices.CONTA_PARA_CONTATO.value:
            # Registros com data_retorno vêm primeiro, ordenados por data (ASC)
            # Registros sem data_retorno vêm depois
            from django.db.models import F
            registros_status = registros_status.order_by(
                F('data_retorno').asc(nulls_last=True),
                '-atualizado_em'
            )
        else:
            registros_status = registros_status.order_by('-atualizado_em')
        
        kanban_counts[status_key] = registros_status.count()
        kanban_by_status[status_key] = registros_status[:8]
    
    flash_success = request.session.pop('flash_success', None)
    flash_error = request.session.pop('flash_error', None)

    # Vendedores disponíveis para filtro (apenas admin)
    from django.contrib.auth.models import User
    vendedores = User.objects.filter(groups__name='Comercial').order_by('first_name', 'username') if user.is_superuser else []

    context = {
        'backlog': backlog,
        'backlog_count': backlog_count,
        'kanban_by_status': kanban_by_status,
        'kanban_counts': kanban_counts,
        'kanban_status_choices': KANBAN_STATUSES,
        'origem_choices': OrigemChoices.choices,
        'canal_choices': CanalContatoChoices.choices,
        'flash_success': flash_success,
        'flash_error': flash_error,
        'vendedores': vendedores,
        'vendedor_filter': vendedor_filter,
    }
    
    # DEBUG: Log do context para verificação
    import sys
    print(f"[KANBAN_CONTEXT] kanban_by_status keys: {kanban_by_status.keys()}", file=sys.stderr)
    for key, regs in kanban_by_status.items():
        print(f"[KANBAN_CONTEXT] {key}: {regs.count()} registros", file=sys.stderr)
    
    return render(request, 'crm/kanban.html', context)


@login_required
@require_POST
def criar_registro(request):
    """Cria um novo registro comercial via formulário."""
    if request.method == 'POST':
        try:
            print("\n==== CRIAR REGISTRO - INICIANDO ====")
            # Extrai dados do POST
            nome = request.POST.get('nome_empresa', '').strip()
            telefone = request.POST.get('telefone', '').strip()
            cidade = request.POST.get('cidade', '').strip()
            uf = request.POST.get('uf', '').strip().upper()
            origem = request.POST.get('origem', OrigemChoices.OUTROS)
            canal_contato = request.POST.get('canal_contato', CanalContatoChoices.WHATSAPP)
            status_cliente = request.POST.get('status_cliente', 'novo').strip()
            codigo_winthor = request.POST.get('codigo_winthor', '').strip()
            
            print(f"Dados recebidos: nome={nome}, telefone={telefone}, cidade={cidade}, uf={uf}")
            print(f"origem={origem}, canal={canal_contato}, status={status_cliente}, winthor={codigo_winthor}")
            print(f"User: {request.user}, is_authenticated: {request.user.is_authenticated}")
            
            # Validar dados obrigatórios
            if not nome or not telefone or not cidade or not uf:
                error_msg = 'Nome, telefone, cidade e UF são obrigatórios'
                print(f"ERRO: Validação falhou - {error_msg}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'error': error_msg}, status=400)
                # Retornar para kanban com mensagem de erro (será exibida pelo JavaScript)
                return redirect('kanban')
            
            # Validar status_cliente
            valid_status = ['novo', 'ativo', 'inativo']
            if status_cliente not in valid_status:
                print(f"Status do cliente inválido: {status_cliente}, usando 'novo'")
                status_cliente = 'novo'
            
            # Validar origem
            if origem not in dict(OrigemChoices.choices):
                print(f"Origem inválida: {origem}, usando OUTROS")
                origem = OrigemChoices.OUTROS
            
            # Validar canal de contato
            if canal_contato not in dict(CanalContatoChoices.choices):
                print(f"Canal inválido: {canal_contato}, usando WHATSAPP")
                canal_contato = CanalContatoChoices.WHATSAPP
            
            print("Tentando criar registro...")
            # Cria o registro
            registro = RegistroComercial.objects.create(
                nome_empresa=nome,
                telefone=telefone,
                cidade=cidade,
                uf=uf,
                origem=origem,
                canal_contato=canal_contato,
                status_cliente=status_cliente,
                codigo_winthor=codigo_winthor if codigo_winthor else None,
                vendedor=request.user,
                status_pipeline=StatusPipelineChoices.CONTA_PARA_CONTATO,
                no_kanban=True
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'registro_id': str(registro.id)})
            return redirect('kanban')
        
        except Exception as e:
            # LOGGING DO ERRO PARA DEBUG
            import traceback
            print(f"\n\n==== ERRO AO CRIAR REGISTRO ====")
            print(f"ERRO: {e}")
            print(f"TIPO: {type(e)}")
            print("TRACEBACK:")
            traceback.print_exc()
            print("=" * 50)
            
            error_msg = f'Erro ao criar registro: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': error_msg}, status=500)
            return redirect('kanban')
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)


@login_required
@require_POST
def mover_para_kanban(request, registro_id):
    """Move um registro do backlog para o Kanban."""
    registro = get_object_or_404(RegistroComercial, id=registro_id)
    
    # Verificar permissão
    if not request.user.is_superuser and registro.vendedor != request.user:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    registro.no_kanban = True
    registro.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('kanban')


@login_required
@require_POST
def mover_para_backlog(request, registro_id):
    """Move um registro do Kanban para o backlog."""
    registro = get_object_or_404(RegistroComercial, id=registro_id)
    
    # Verificar permissão
    if not request.user.is_superuser and registro.vendedor != request.user:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    registro.mover_para_backlog()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('kanban')


@login_required
@require_POST
def atualizar_status(request, registro_id):
    """Atualiza o status de um registro via drag & drop."""
    registro = get_object_or_404(RegistroComercial, id=registro_id)
    
    # Verificar permissão
    if not request.user.is_superuser and registro.vendedor != request.user:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    novo_status = request.POST.get('novo_status')

    if novo_status not in dict(StatusPipelineChoices.choices):
        return JsonResponse({'error': 'Status inválido'}, status=400)

    if novo_status == registro.status_pipeline:
        return JsonResponse({'error': 'O registro já está neste estágio.'}, status=400)

    if novo_status not in allowed_transitions(registro.status_pipeline):
        return JsonResponse({'error': 'Transição não permitida. Use "Registrar Contato" para avançar ou retornar.'}, status=400)

    # Regra global: mudar estágio exige um contato registrado no fluxo oficial
    return JsonResponse({'error': 'Registro de contato obrigatório para mudar estágio. Use "Registrar Contato".'}, status=400)


@login_required
def registrar_contato(request, registro_id):
    """Registra um novo contato com pipeline automático."""
    registro = get_object_or_404(RegistroComercial, id=registro_id)
    
    # Verificar permissão
    if not request.user.is_superuser and registro.vendedor != request.user:
        return redirect('kanban')
    
    # Buscar regras do pipeline para o estágio atual
    raw_status = registro.status_pipeline
    current_stage = STATUS_PIPELINE_MAP.get(raw_status)
    pipeline_rules = PIPELINE_RULES.get(current_stage, {})
    
    # ✅ FORMATO FINAL: Array de {key, label, next_status_label} (Opção A canônica)
    # Se estamos em "Conta para Contato", usar opções conforme status_cliente
    if current_stage == 'CONTA_PARA_CONTATO':
        # Carregar opções dinâmicas conforme status do cliente
        valid_resultado_keys = RESULTADO_POR_STATUS_CLIENTE.get(registro.status_cliente, 
                                                               RESULTADO_POR_STATUS_CLIENTE.get('novo', []))
    else:
        # Para outros estágios, usar opções do pipeline normal
        valid_resultado_keys = list(pipeline_rules.get('results', {}).keys())
    
    results = []
    for k in valid_resultado_keys:
        # Para "Conta para Contato", buscar next_stage do pipeline_rules (pode ter mudado)
        if current_stage == 'CONTA_PARA_CONTATO':
            next_stage = pipeline_rules.get('results', {}).get(k, 'CONTA_PARA_CONTATO')
        else:
            next_stage = pipeline_rules.get('results', {}).get(k, current_stage)
        
        # Converter estágio do pipeline para valor do banco antes de pegar label
        db_next_stage = PIPELINE_TO_DB_MAP.get(next_stage, next_stage)
        next_stage_label = dict(StatusPipelineChoices.choices).get(db_next_stage, db_next_stage)
        
        results.append({
            "key": k,
            "label": RESULT_LABELS.get(k, k),
            "next_status_label": next_stage_label
        })
    
    checklist = [
        [item, CHECKLIST_LABELS.get(item, item)]
        for item in pipeline_rules.get('checklist', [])
    ]

    if request.method == 'POST':
        resultado_code = request.POST.get('resultado', '').strip()
        checklist_itens = request.POST.getlist('checklist')
        canal_contato = request.POST.get('canal_contato', registro.canal_contato)
        proximo_passo = request.POST.get('proximo_passo', '').strip()
        data_retorno_str = request.POST.get('data_retorno', '').strip()
        periodo_retorno = request.POST.get('periodo_retorno', '').strip()
        observacoes = request.POST.get('observacoes', '').strip()

        # Validar canal
        if canal_contato not in dict(CanalContatoChoices.choices):
            return render(request, 'crm/registrar_contato.html', {
                'registro': registro,
                'error': 'Canal de contato inválido.',
                'canal_choices': CanalContatoChoices.choices,
                'results_json': json.dumps(results),
                'checklist_json': json.dumps(checklist),
            })
        
        # Validar resultado obrigatório
        if not resultado_code:
            return render(request, 'crm/registrar_contato.html', {
                'registro': registro,
                'error': 'Selecione um resultado.',
                'canal_choices': CanalContatoChoices.choices,
                'results_json': json.dumps(results),
                'checklist_json': json.dumps(checklist),
            })

        # Validar resultado no ENUM do estágio (com suporte a status_cliente)
        if current_stage == 'CONTA_PARA_CONTATO':
            # Para "Conta para Contato", validar apenas contra as opções do status_cliente
            valid_resultado_keys = RESULTADO_POR_STATUS_CLIENTE.get(registro.status_cliente, 
                                                                   RESULTADO_POR_STATUS_CLIENTE.get('novo', []))
            if resultado_code not in valid_resultado_keys:
                return render(request, 'crm/registrar_contato.html', {
                    'registro': registro,
                    'error': f'Resultado inválido para cliente {registro.status_cliente}.',
                    'canal_choices': CanalContatoChoices.choices,
                    'results_json': json.dumps(results),
                    'checklist_json': json.dumps(checklist),
                })
        else:
            # Para outros estágios, usar validação normal
            valid_results = pipeline_rules.get('results', {})
            if resultado_code not in valid_results:
                return render(request, 'crm/registrar_contato.html', {
                    'registro': registro,
                    'error': 'Resultado inválido para este estágio.',
                    'canal_choices': CanalContatoChoices.choices,
                    'results_json': json.dumps(results),
                    'checklist_json': json.dumps(checklist),
                })

        # Converter checklist para dict {item: True}
        checklist_dict = {item: True for item in checklist_itens}
        
        # Resolver próximo estágio via pipeline module
        try:
            next_stage = resolve_next_stage(current_stage, resultado_code, checklist_dict)
        except ValueError as e:
            return render(request, 'crm/registrar_contato.html', {
                'registro': registro,
                'error': str(e),
                'canal_choices': CanalContatoChoices.choices,
                'results_json': json.dumps(results),
                'checklist_json': json.dumps(checklist),
            })

        status_anterior = registro.status_pipeline

        # Converter estágio do pipeline (MAIÚSCULO) para valor oficial do banco (minúsculo)
        db_next_stage = PIPELINE_TO_DB_MAP.get(next_stage, registro.status_pipeline)

        # Processar data de retorno (se fornecida)
        data_retorno = None
        
        # Se resultado for "responsavel_indisponivel" OU proximo_passo contiver "Retornar contato"
        if resultado_code == 'responsavel_indisponivel' or 'Retornar contato' in proximo_passo:
            print(f"DEBUG: Processando retorno - data_retorno_str={data_retorno_str}, periodo={periodo_retorno}")
            
            # Data é obrigatória
            if not data_retorno_str:
                print("DEBUG: Data vazia - erro")
                return render(request, 'crm/registrar_contato.html', {
                    'registro': registro,
                    'error': 'Data de retorno é obrigatória quando responsável está indisponível.',
                    'canal_choices': CanalContatoChoices.choices,
                    'results_json': json.dumps(results),
                    'checklist_json': json.dumps(checklist),
                    'next_steps': next_steps,
                })
            
            # Período é obrigatório
            if not periodo_retorno:
                print("DEBUG: Período vazio - erro")
                return render(request, 'crm/registrar_contato.html', {
                    'registro': registro,
                    'error': 'Período de retorno é obrigatório (Manhã ou Tarde).',
                    'canal_choices': CanalContatoChoices.choices,
                    'results_json': json.dumps(results),
                    'checklist_json': json.dumps(checklist),
                    'next_steps': next_steps,
                })
            
            from datetime import datetime
            try:
                # Aceitar apenas formato date (YYYY-MM-DD)
                data_retorno = datetime.strptime(data_retorno_str, '%Y-%m-%d')
                # Tornar timezone-aware
                data_retorno = timezone.make_aware(data_retorno)
                print(f"DEBUG: Data parseada com sucesso: {data_retorno}")
            except ValueError as e:
                print(f"DEBUG: Erro ao parsear data: {e}")
                return render(request, 'crm/registrar_contato.html', {
                    'registro': registro,
                    'error': f'Data de retorno inválida: {data_retorno_str}',
                    'canal_choices': CanalContatoChoices.choices,
                    'results_json': json.dumps(results),
                    'checklist_json': json.dumps(checklist),
                    'next_steps': next_steps,
                })
            
            # Definir proximo_passo com período
            proximo_passo = f"Retornar contato (data combinada) - {periodo_retorno}"
            print(f"DEBUG: proximo_passo definido como: {proximo_passo}")
        else:
            # Não é retorno agendado - limpar data_retorno
            data_retorno = None
            print(f"DEBUG: Não é retorno, limpando data_retorno")

        # Atualizar registro
        registro.ultimo_contato = timezone.now()
        registro.resultado_ultimo_contato = resultado_code
        registro.proximo_passo = proximo_passo  # USAR proximo_passo!
        registro.canal_contato = canal_contato
        registro.status_pipeline = db_next_stage
        registro.data_retorno = data_retorno
        
        print(f"SAVE: resultado={resultado_code} | data={data_retorno} | passo={proximo_passo}")

        # Arquivar se necessário
        if db_next_stage == StatusPipelineChoices.ARQUIVADA.value:
            registro.no_kanban = False

        registro.save()

        # Registrar histórico
        # Formato: "Resultado: X" + observações se fornecidas
        resultado_texto = RESULT_LABELS.get(resultado_code, resultado_code)
        if observacoes:
            resultado_com_obs = f"{resultado_texto}\n\nObservações: {observacoes}"
        else:
            resultado_com_obs = resultado_texto
        
        ContatoHistorico.objects.create(
            registro=registro,
            data_contato=registro.ultimo_contato,
            resultado=resultado_com_obs,
            status_anterior=status_anterior,
            status_novo=registro.status_pipeline,
            usuario=request.user,
            canal_contato=canal_contato,
            checklist_itens=checklist_itens,
        )

        # ✅ Auto-arquivar após 2 "responsavel_indisponivel"
        if resultado_code == 'responsavel_indisponivel':
            # Contar ocorrências de "responsavel_indisponivel" (procura pelo padrão no resultado salvo)
            retornos = ContatoHistorico.objects.filter(
                registro=registro,
                resultado__icontains='Responsável não disponível'
            ).count()
            
            print(f"Retornos: {retornos}")
            if retornos >= 2:
                print(f"🔴 ARQUIVANDO")
                registro.status_pipeline = StatusPipelineChoices.ARQUIVADA.value
                registro.no_kanban = False
                registro.save()
                ContatoHistorico.objects.create(
                    registro=registro,
                    data_contato=timezone.now(),
                    resultado='arquivado_automatico',
                    status_anterior=status_anterior,
                    status_novo=StatusPipelineChoices.ARQUIVADA.value,
                    usuario=request.user,
                    canal_contato=canal_contato,
                    checklist_itens=[],
                )

        return redirect('kanban')

    # GET request - renderizar formulário
    # Buscar next_steps do estágio atual (STAGE_CONFIG)
    stage_config = STAGE_CONFIG.get(raw_status, {})
    next_steps = stage_config.get('next_steps', [])
    
    context = {
        'registro': registro,
        'canal_choices': CanalContatoChoices.choices,
        'results_json': json.dumps(results),
        'checklist_json': json.dumps(checklist),
        'next_steps': next_steps,
    }

    return render(request, 'crm/registrar_contato.html', context)


@login_required
def registrar_contato_htmx(request, registro_id):
    """Registra contato e retorna card atualizado para HTMX."""
    registro = get_object_or_404(RegistroComercial, id=registro_id)
    
    # Verificar permissão
    if not request.user.is_superuser and registro.vendedor != request.user:
        return HttpResponse('Acesso negado', status=403)
    
    if request.method == 'POST':
        resultado = request.POST.get('resultado', '').strip()
        novo_status = request.POST.get('novo_status')
        proximo_passo = request.POST.get('proximo_passo', '').strip()
        checklist_itens = request.POST.getlist('checklist')
        canal_contato = request.POST.get('canal_contato', registro.canal_contato)

        allowed_statuses = allowed_transitions(registro.status_pipeline)
        stage_cfg = STAGE_CONFIG.get(novo_status, {})

        if canal_contato not in dict(CanalContatoChoices.choices):
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Canal de contato inválido.</div>',
                status=400
            )

        if not novo_status:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Atualizar Status é obrigatório.</div>',
                status=400
            )

        if novo_status not in dict(StatusPipelineChoices.choices):
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Status inválido.</div>',
                status=400
            )

        if novo_status == registro.status_pipeline:
            return HttpResponse(
                f'<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">O novo status não pode ser igual ao status atual ({registro.get_status_pipeline_display()}).</div>',
                status=400
            )

        if novo_status not in allowed_statuses:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Transição não permitida para este estágio.</div>',
                status=400
            )

        if not resultado:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">O campo resultado é obrigatório.</div>',
                status=400
            )

        if stage_cfg.get('require_next_step') and not proximo_passo and novo_status != StatusPipelineChoices.ARQUIVADA.value:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Selecione o Próximo Passo (lista fechada).</div>',
                status=400
            )

        if proximo_passo and proximo_passo not in stage_cfg.get('next_steps', []) and novo_status != StatusPipelineChoices.ARQUIVADA.value:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Próximo passo inválido para este estágio.</div>',
                status=400
            )

        if stage_cfg.get('require_checklist') and len(checklist_itens) == 0:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Marque ao menos um item do checklist.</div>',
                status=400
            )

        if any(item not in stage_cfg.get('checklist', []) for item in checklist_itens):
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Checklist inválido para este estágio.</div>',
                status=400
            )

        if novo_status == StatusPipelineChoices.NEGOCIACAO_COTACAO.value and not any(
            item in checklist_itens for item in ['Cotação enviada', 'Follow-up realizado']
        ):
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Registre Cotação enviada ou Follow-up realizado para entrar em Negociação/Cotação.</div>',
                status=400
            )

        if novo_status == StatusPipelineChoices.PEDIDO_REALIZADO.value and len(checklist_itens) == 0:
            return HttpResponse(
                '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">Confirme o pedido marcando itens do checklist.</div>',
                status=400
            )

        if novo_status == StatusPipelineChoices.ARQUIVADA.value:
            proximo_passo = ''

        status_anterior = registro.status_pipeline

        registro.ultimo_contato = timezone.now()
        registro.resultado_ultimo_contato = resultado
        registro.proximo_passo = proximo_passo
        registro.canal_contato = canal_contato
        registro.status_pipeline = novo_status

        if novo_status == StatusPipelineChoices.ARQUIVADA.value:
            registro.no_kanban = False

        registro.save()

        ContatoHistorico.objects.create(
            registro=registro,
            data_contato=registro.ultimo_contato,
            resultado=resultado,
            status_anterior=status_anterior,
            status_novo=registro.status_pipeline,
            usuario=request.user,
            canal_contato=canal_contato,
            checklist_itens=checklist_itens,
        )

        card_html = render_to_string('crm/_card.html', {'registro': registro})
        response = HttpResponse(card_html)
        response['HX-Trigger'] = json.dumps({
            'cardUpdated': {
                'cardId': str(registro.id),
                'oldStatus': status_anterior,
                'newStatus': novo_status,
                'statusLabel': registro.get_status_pipeline_display()
            }
        })
        return response

    return HttpResponse('Método não permitido', status=405)


@comercial_required
@login_required(login_url='login')
def metricas_view(request):
    """View de métricas - apenas ADMIN."""
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
        return redirect('login')
    user = request.user
    
    from datetime import datetime, timedelta
    
    vendedor_filter = request.GET.get('vendedor')
    periodo = request.GET.get('periodo', 'dia')  # Default: dia
    origem_filter = request.GET.get('origem')  # Novo: filtro por origem
    status_filter = request.GET.get('status')  # Novo: filtro por status
    
    # Calcular datas baseado no período
    now = timezone.now()
    today = now.date()
    
    if periodo == 'semana':
        # Última semana (7 dias)
        data_inicio = today - timedelta(days=7)
    elif periodo == 'mes':
        # Último mês (30 dias)
        data_inicio = today - timedelta(days=30)
    else:  # dia (padrão)
        # Hoje apenas
        data_inicio = today

    # Filtrar por vendedor ou todos (se gestor)
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        base_registros = RegistroComercial.objects.all()
        contatos = ContatoHistorico.objects.all()

        if vendedor_filter and vendedor_filter != 'todos':
            base_registros = base_registros.filter(vendedor_id=vendedor_filter)
            contatos = contatos.filter(usuario_id=vendedor_filter)

        vendedores = User.objects.filter(groups__name='Comercial').distinct().order_by('first_name', 'username')
    else:
        base_registros = RegistroComercial.objects.filter(vendedor=user)
        contatos = ContatoHistorico.objects.filter(usuario=user)
        vendedores = []
    
    # Filtrar por período (considerando atualizado_em dos registros - atividade)
    base_registros = base_registros.filter(atualizado_em__date__gte=data_inicio)
    
    # Métricas apenas de trabalho ativo (no_kanban=True OU status especial: Conta Ativa ou Arquivada)
    registros = base_registros.filter(
        Q(no_kanban=True) | 
        Q(status_pipeline=StatusPipelineChoices.CONTA_ATIVA.value) |
        Q(status_pipeline=StatusPipelineChoices.ARQUIVADA.value)
    )
    
    # FILTROS AVANÇADOS
    if origem_filter and origem_filter != '':
        registros = registros.filter(origem=origem_filter)
    
    if status_filter and status_filter != '':
        registros = registros.filter(status_pipeline=status_filter)
    
    # Backlog (aguardando entrada no Kanban)
    backlog_count = base_registros.filter(no_kanban=False).exclude(
        status_pipeline__in=[StatusPipelineChoices.CONTA_ATIVA.value, StatusPipelineChoices.ARQUIVADA.value]
    ).count()
    
    # Métricas por status (pipeline)
    metricas_status = {}
    for status_enum, status_label in PIPELINE_SEQUENCE:
        metricas_status[status_label] = registros.filter(status_pipeline=status_enum.value).count()
    
    total_leads = registros.count()
    conta_para_contato = metricas_status.get(StatusPipelineChoices.CONTA_PARA_CONTATO.label, 0)
    contatos_realizados = metricas_status.get(StatusPipelineChoices.CONTATO_FEITO.label, 0)
    negociacoes = metricas_status.get(StatusPipelineChoices.NEGOCIACAO_COTACAO.label, 0)
    pedidos = metricas_status.get(StatusPipelineChoices.PEDIDO_REALIZADO.label, 0)
    contas_ativas = metricas_status.get(StatusPipelineChoices.CONTA_ATIVA.label, 0)

    # Cidades e Estados onde estamos trabalhando - COM PAGINAÇÃO
    cidades_estados_all = registros.values('cidade', 'uf').annotate(count=Count('id')).order_by('-count')
    
    paginator = Paginator(cidades_estados_all, 20)  # 20 cidades por página
    page = request.GET.get('cidades_page')
    
    try:
        cidades_estados = paginator.page(page)
    except PageNotAnInteger:
        cidades_estados = paginator.page(1)
    except EmptyPage:
        cidades_estados = paginator.page(paginator.num_pages)
    
    # Origem dos contatos
    origem_stats = []
    for origem_key, origem_label in OrigemChoices.choices:
        count = registros.filter(origem=origem_key).count()
        if count > 0:
            origem_stats.append((origem_key, origem_label, count))
    origem_stats.sort(key=lambda x: x[2], reverse=True)
    
    context = {
        'metricas_status': metricas_status,
        'total_leads': total_leads,
        'conta_para_contato': conta_para_contato,
        'contatos_realizados': contatos_realizados,
        'negociacoes': negociacoes,
        'pedidos': pedidos,
        'contas_ativas': contas_ativas,
        'cidades_estados': cidades_estados,
        'cidades_paginator': paginator,
        'cidades_page_obj': cidades_estados,
        'origem_stats': origem_stats,
        'backlog_count': backlog_count,
        'vendedores': vendedores,
        'vendedor_filter': vendedor_filter,
        'origem_filter': origem_filter,  # Novo
        'status_filter': status_filter,  # Novo
        'status_choices': StatusPipelineChoices.choices,  # Novo
        'origem_choices': OrigemChoices.choices,  # Novo
        'periodo': periodo,
        'is_admin_user': user.is_superuser or user.groups.filter(name='Admin').exists(),
    }
    
    return render(request, 'crm/metricas.html', context)


@admin_required
@admin_required
def gestao_usuarios(request):
    """View para gestão de usuários e grupos."""
    from django.contrib.auth.models import User, Group
    
    usuarios = User.objects.all().order_by('-date_joined')
    grupos = Group.objects.all()
    
    # Paginação
    paginator = Paginator(usuarios, 20)  # 20 usuários por página
    page = request.GET.get('page')
    
    try:
        usuarios_page = paginator.page(page)
    except PageNotAnInteger:
        usuarios_page = paginator.page(1)
    except EmptyPage:
        usuarios_page = paginator.page(paginator.num_pages)
    
    context = {
        'usuarios': usuarios_page,
        'paginator': paginator,
        'page_obj': usuarios_page,
        'grupos': grupos,
    }
    
    return render(request, 'crm/gestao_usuarios.html', context)


@comercial_required
def meu_desempenho(request):
    """Dashboard de desempenho personalizado do vendedor."""
    user = request.user
    
    # Buscar registros do vendedor
    registros = RegistroComercial.objects.filter(vendedor=user)
    base_registros = registros
    
    # Métricas principais
    total_leads = registros.count()
    contatos_realizados = registros.filter(status_pipeline=StatusPipelineChoices.CONTATO_FEITO.value).count()
    negociacoes = registros.filter(status_pipeline=StatusPipelineChoices.NEGOCIACAO_COTACAO.value).count()
    pedidos = registros.filter(status_pipeline=StatusPipelineChoices.PEDIDO_REALIZADO.value).count()
    contas_ativas = registros.filter(status_pipeline=StatusPipelineChoices.CONTA_ATIVA.value).count()
    conta_para_contato = registros.filter(status_pipeline=StatusPipelineChoices.CONTA_PARA_CONTATO.value).count()
    
    taxa_contato = round((contatos_realizados / total_leads * 100) if total_leads > 0 else 0)
    taxa_negociacao = round((negociacoes / contatos_realizados * 100) if contatos_realizados > 0 else 0)
    taxa_pedido = round((pedidos / negociacoes * 100) if negociacoes > 0 else 0)
    taxa_recorrencia = round((contas_ativas / pedidos * 100) if pedidos > 0 else 0)
    
    pct_conta_para_contato = round((conta_para_contato / total_leads * 100) if total_leads > 0 else 0)
    pct_contato_realizado = round((contatos_realizados / total_leads * 100) if total_leads > 0 else 0)
    pct_negociacao = round((negociacoes / total_leads * 100) if total_leads > 0 else 0)
    pct_pedido = round((pedidos / total_leads * 100) if total_leads > 0 else 0)
    pct_conta_ativa = round((contas_ativas / total_leads * 100) if total_leads > 0 else 0)
    
    # Origem dos leads
    origem_stats = []
    for origem_key, origem_label in OrigemChoices.choices:
        count = registros.filter(origem=origem_key).count()
        if count > 0:
            origem_stats.append((origem_label, count))
    
    origem_stats.sort(key=lambda x: x[1], reverse=True)
    
    # Backlog (aguardando entrada no Kanban)
    backlog_count = base_registros.filter(no_kanban=False).exclude(
        status_pipeline__in=[
            StatusPipelineChoices.CONTA_ATIVA.value,
            StatusPipelineChoices.ARQUIVADA.value,
        ]
    ).count()

    # Cidades e Estados trabalhados (top 10)
    cidades_estados = list(
        base_registros.values('cidade', 'uf').annotate(count=Count('id')).order_by('-count')[:10]
    )

    hoje = timezone.now()
    
    context = {
        'total_leads': total_leads,
        'contatos_realizados': contatos_realizados,
        'negociacoes': negociacoes,
        'pedidos': pedidos,
        'contas_ativas': contas_ativas,
        'contatos_realizados': contatos_realizados,
        'conta_para_contato': conta_para_contato,
        'backlog_count': backlog_count,
        'taxa_contato': taxa_contato,
        'taxa_negociacao': taxa_negociacao,
        'taxa_pedido': taxa_pedido,
        'taxa_recorrencia': taxa_recorrencia,
        'pct_conta_para_contato': pct_conta_para_contato,
        'pct_contato_realizado': pct_contato_realizado,
        'pct_negociacao': pct_negociacao,
        'pct_pedido': pct_pedido,
        'pct_conta_ativa': pct_conta_ativa,
        'origem_stats': origem_stats,
        'cidades_estados': cidades_estados,
        'hoje': hoje,
    }
    
    return render(request, 'crm/meu_desempenho.html', context)


@admin_required
def importar_csv_view(request):
    """View para importação de CSV."""
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        
        # SEGURANÇA: Validar tamanho do arquivo (máximo 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            context = {
                'error': 'Arquivo muito grande. Máximo 5MB.',
                'origem_choices': OrigemChoices.choices,
                'canal_choices': CanalContatoChoices.choices,
            }
            return render(request, 'crm/importar_csv.html', context)
        
        # SEGURANÇA: Validar extensão do arquivo
        if not csv_file.name.endswith('.csv'):
            context = {
                'error': 'Arquivo deve ter extensão .csv',
                'origem_choices': OrigemChoices.choices,
                'canal_choices': CanalContatoChoices.choices,
            }
            return render(request, 'crm/importar_csv.html', context)
        
        # SEGURANÇA: Validar tipo MIME
        allowed_mime_types = ['text/csv', 'application/vnd.ms-excel', 'text/plain']
        if csv_file.content_type not in allowed_mime_types:
            context = {
                'error': 'Tipo de arquivo inválido. Envie um arquivo CSV válido.',
                'origem_choices': OrigemChoices.choices,
                'canal_choices': CanalContatoChoices.choices,
            }
            return render(request, 'crm/importar_csv.html', context)
        
        try:
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            importados = 0
            erros = []
            
            for row in reader:
                try:
                    # Validar campos obrigatórios
                    if not all([row.get('nome_empresa'), row.get('telefone'), 
                               row.get('cidade'), row.get('uf'), row.get('origem'), row.get('canal_contato')]):
                        erros.append(f"Linha com dados faltando: {row}")
                        continue
                    
                    canal_contato = row.get('canal_contato', CanalContatoChoices.WHATSAPP)
                    if canal_contato not in dict(CanalContatoChoices.choices):
                        erros.append(f"Canal inválido na linha: {row}")
                        continue

                    # Criar registro
                    RegistroComercial.objects.create(
                        nome_empresa=row['nome_empresa'],
                        telefone=row['telefone'],
                        cidade=row['cidade'],
                        uf=row['uf'],
                        origem=row['origem'],
                        canal_contato=canal_contato,
                        codigo_winthor=row.get('codigo_winthor', ''),
                        vendedor=request.user,
                        status_pipeline=StatusPipelineChoices.CONTA_PARA_CONTATO.value
                    )
                    importados += 1
                    
                except Exception as e:
                    erros.append(f"Erro na linha {row}: {str(e)}")
            
            context = {
                'importados': importados,
                'erros': erros,
                'origem_choices': OrigemChoices.choices,
                'canal_choices': CanalContatoChoices.choices,
            }
            
            return render(request, 'crm/importar_csv.html', context)
            
        except Exception as e:
            context = {
                'error': f'Erro ao processar arquivo: {str(e)}',
                'origem_choices': OrigemChoices.choices,
                'canal_choices': CanalContatoChoices.choices,
            }
            return render(request, 'crm/importar_csv.html', context)
    
    context = {
        'origem_choices': OrigemChoices.choices,
        'canal_choices': CanalContatoChoices.choices,
    }
    return render(request, 'crm/importar_csv.html', context)


@api_login_required
def desempenho_vendedor_api(request, vendedor_id):
    """API endpoint para buscar desempenho de um vendedor específico ou de todos."""
    from django.contrib.auth.models import User
    from django.utils import timezone
    from datetime import timedelta
    import json
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"[DESEMPENHO_API] Requisição recebida - Method: {request.method}")
    logger.info(f"[DESEMPENHO_API] User ID: {request.user.id} (tipo: {type(request.user.id).__name__})")
    logger.info(f"[DESEMPENHO_API] Vendedor ID: {vendedor_id} (tipo: {type(vendedor_id).__name__})")
    logger.info(f"[DESEMPENHO_API] Is superuser: {request.user.is_superuser}")
    logger.info(f"[DESEMPENHO_API] Comparação: {request.user.id} == {vendedor_id} = {request.user.id == vendedor_id}")
    
    # Verificar método HTTP
    if request.method != 'POST':
        logger.warning(f"[DESEMPENHO_API] Método inválido: {request.method}")
        return JsonResponse({'error': f'Método {request.method} não permitido. Use POST.'}, status=405)
    
    # SEGURANÇA: Verificar se o usuário tem permissão de acessar estes dados
    if not request.user.is_superuser and request.user.id != vendedor_id:
        logger.warning(f"[DESEMPENHO_API] Acesso negado - User ID: {request.user.id}, Vendedor ID: {vendedor_id}")
        return JsonResponse({
            'error': 'Sem permissão para acessar dados deste vendedor',
            'debug': f'user_id={request.user.id}, vendedor_id={vendedor_id}, superuser={request.user.is_superuser}'
        }, status=403)
    
    try:
        # Se é admin, retornar dados de TODOS os vendedores
        # Se não é admin, retornar apenas dados do próprio usuário
        if request.user.is_superuser:
            # Admin vê dados de todos
            registros_query = RegistroComercial.objects.all()
            vendedor_nome = "Todos os Vendedores"
        else:
            # Vendedor vê apenas seus próprios dados
            registros_query = RegistroComercial.objects.filter(vendedor=request.user)
            vendedor_nome = request.user.get_full_name() or request.user.username
        
        # Obter período do filtro
        periodo = 'dia'  # padrão
        if request.body:
            try:
                data = json.loads(request.body)
                periodo = data.get('periodo', 'dia')
            except:
                pass
        
        # Calcular data de início baseado no período
        hoje = timezone.now().date()  # Apenas a data, sem hora
        
        if periodo == 'dia':
            # Filtra por registros de HOJE (mesma data, independente hora)
            registros = registros_query.filter(
                criado_em__date=hoje
            ).distinct()
        elif periodo == 'semana':
            # Início da semana (segunda-feira) até agora
            inicio_semana = hoje - timedelta(days=hoje.weekday())
            registros = registros_query.filter(
                criado_em__date__gte=inicio_semana
            ).distinct()
        elif periodo == 'mes':
            # Início do mês até agora
            inicio_mes = hoje.replace(day=1)
            registros = registros_query.filter(
                criado_em__date__gte=inicio_mes
            ).distinct()
        else:
            # Default: dia
            registros = registros_query.filter(
                criado_em__date=hoje
            ).distinct()
        
        total_leads = registros.count()
        conta_para_contato = registros.filter(status_pipeline=StatusPipelineChoices.CONTA_PARA_CONTATO.value).count()
        contatos_realizados = registros.filter(status_pipeline=StatusPipelineChoices.CONTATO_FEITO.value).count()
        negociacoes = registros.filter(status_pipeline=StatusPipelineChoices.NEGOCIACAO_COTACAO.value).count()
        pedidos = registros.filter(status_pipeline=StatusPipelineChoices.PEDIDO_REALIZADO.value).count()
        contas_ativas = registros.filter(status_pipeline=StatusPipelineChoices.CONTA_ATIVA.value).count()
        
        taxa_contato = round((contatos_realizados / total_leads * 100) if total_leads > 0 else 0)
        taxa_negociacao = round((negociacoes / contatos_realizados * 100) if contatos_realizados > 0 else 0)
        taxa_pedido = round((pedidos / negociacoes * 100) if negociacoes > 0 else 0)
        taxa_recorrencia = round((contas_ativas / pedidos * 100) if pedidos > 0 else 0)
        
        return JsonResponse({
            'vendedor_nome': vendedor_nome,
            'total_leads': total_leads,
            'conta_para_contato': conta_para_contato,
            'contatos_realizados': contatos_realizados,
            'negociacoes': negociacoes,
            'pedidos': pedidos,
            'contas_ativas': contas_ativas,
            'taxa_contato': taxa_contato,
            'taxa_negociacao': taxa_negociacao,
            'taxa_pedido': taxa_pedido,
            'taxa_recorrencia': taxa_recorrencia,
        })
    except User.DoesNotExist:
        logger.error(f"[DESEMPENHO_API] Vendedor não encontrado: {vendedor_id}")
        return JsonResponse({'error': 'Vendedor não encontrado'}, status=404)
    except Exception as e:
        logger.error(f"[DESEMPENHO_API] Erro inesperado: {str(e)}", exc_info=True)
        return JsonResponse({'error': f'Erro ao processar requisição: {str(e)}'}, status=500)


@api_comercial_required
def carregar_mais_registros_api(request):
    """API para carregar mais registros paginados."""
    user = request.user
    pagina = int(request.GET.get('page', 1))
    local = request.GET.get('local', 'backlog')  # backlog ou status_key (ex: a_trabalhar)
    registros_por_pagina = 8
    offset = (pagina - 1) * registros_por_pagina
    
    # Filtrar registros por vendedor (a menos que seja gestor)
    if user.is_superuser:
        all_registros = RegistroComercial.objects.all()
    else:
        all_registros = RegistroComercial.objects.filter(vendedor=user)
    
    if local == 'backlog':
        # Backlog: registros não ativos
        registros = all_registros.filter(no_kanban=False).order_by('-criado_em')[offset:offset+registros_por_pagina]
        total = all_registros.filter(no_kanban=False).count()
    else:
        # Status específico do Kanban
        registros = all_registros.filter(
            no_kanban=True, 
            status_pipeline=local
        ).exclude(status_pipeline=StatusPipelineChoices.ARQUIVADA.value).order_by('-ultimo_contato')[offset:offset+registros_por_pagina]
        total = all_registros.filter(
            no_kanban=True, 
            status_pipeline=local
        ).exclude(status_pipeline=StatusPipelineChoices.ARQUIVADA.value).count()
    
    # Renderizar cards HTML
    cards_html = render_to_string('crm/partials/registro_cards.html', {
        'registros': registros,
        'local': local,
    })
    
    return JsonResponse({
        'html': cards_html,
        'total': total,
        'offset': offset + registros_por_pagina,
        'tem_mais': (offset + registros_por_pagina) < total,
    })


@admin_required
def arquivados_view(request):
    """View para listar leads arquivados - ADMIN ONLY."""
    user = request.user
    
    # Filtrar arquivados por vendedor (a menos que seja gestor)
    if user.is_superuser:
        arquivados = RegistroComercial.objects.filter(status_pipeline=StatusPipelineChoices.ARQUIVADA)
    else:
        arquivados = RegistroComercial.objects.filter(vendedor=user, status_pipeline=StatusPipelineChoices.ARQUIVADA)
    
    arquivados = arquivados.order_by('-atualizado_em')
    
    # Paginação
    paginator = Paginator(arquivados, 15)  # 15 itens por página
    page = request.GET.get('page')
    
    try:
        arquivados_page = paginator.page(page)
    except PageNotAnInteger:
        arquivados_page = paginator.page(1)
    except EmptyPage:
        arquivados_page = paginator.page(paginator.num_pages)
    
    flash_success = request.session.pop('flash_success', None)
    
    context = {
        'arquivados': arquivados_page,
        'paginator': paginator,
        'page_obj': arquivados_page,
        'flash_success': flash_success,
    }
    
    return render(request, 'crm/arquivados.html', context)


@comercial_required
def contas_ativas_view(request):
    """Lista contas ativas (recorrência) fora do Kanban."""
    user = request.user

    if user.is_superuser:
        contas = RegistroComercial.objects.filter(status_pipeline=StatusPipelineChoices.CONTA_ATIVA.value)
    else:
        contas = RegistroComercial.objects.filter(vendedor=user, status_pipeline=StatusPipelineChoices.CONTA_ATIVA.value)

    contas = contas.order_by('-atualizado_em')
    
    # Paginação
    paginator = Paginator(contas, 15)  # 15 itens por página
    page = request.GET.get('page')
    
    try:
        contas_page = paginator.page(page)
    except PageNotAnInteger:
        contas_page = paginator.page(1)
    except EmptyPage:
        contas_page = paginator.page(paginator.num_pages)

    context = {
        'contas': contas_page,
        'paginator': paginator,
        'page_obj': contas_page,
    }

    return render(request, 'crm/contas_ativas.html', context)


@admin_required
@require_POST
def restaurar_lead(request, registro_id):
    """Restaura um lead arquivado para A Trabalhar."""
    registro = get_object_or_404(RegistroComercial, id=registro_id)
    
    # Verificar permissão
    if not request.user.is_superuser and registro.vendedor != request.user:
        return JsonResponse({'error': 'Sem permissão'}, status=403)
    
    # Restaurar para Conta para Contato
    registro.status_pipeline = StatusPipelineChoices.CONTA_PARA_CONTATO.value
    registro.no_kanban = True
    registro.save()
    
    request.session['flash_success'] = f'Lead "{registro.nome_empresa}" restaurado com sucesso!'
    return redirect('arquivados')


@admin_required
@require_POST
@admin_required
def criar_usuario(request):
    """Cria ou edita um usuário."""
    from django.contrib.auth.models import User, Group
    from django.contrib import messages
    
    usuario_id = request.POST.get('usuario_id')
    username = request.POST.get('username')
    email = request.POST.get('email')
    first_name = request.POST.get('first_name')
    password = request.POST.get('password')
    grupo = request.POST.get('grupo')
    is_superuser = request.POST.get('is_superuser') == 'on'
    
    # Modo edição
    if usuario_id:
        user = get_object_or_404(User, id=usuario_id)
        
        # Não permitir editar a si mesmo
        if request.user.id == user.id:
            messages.error(request, 'Você não pode editar sua própria conta!')
            return redirect('gestao_usuarios')
        
        # Atualizar campos
        user.email = email
        user.first_name = first_name
        user.is_superuser = is_superuser
        user.is_staff = is_superuser  # Staff também é true se for superuser
        
        # Alterar senha se fornecida
        if password:
            user.set_password(password)
        
        user.save()
        
        # Atualizar grupo: remover de todos e adicionar novo se especificado
        user.groups.clear()
        if grupo:
            try:
                group = Group.objects.get(name=grupo)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        
        messages.success(request, f'Usuário "{username}" atualizado com sucesso!')
    
    # Modo criação
    else:
        # Validar se usuário já existe
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Usuário "{username}" já existe!')
            return redirect('gestao_usuarios')
        
        # Criar usuário
        if is_superuser:
            # Para superusers, usar create_superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password or 'SenhaTemporaria123',
            )
            user.first_name = first_name
            user.save()
        else:
            # Para usuários normais, usar create_user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                password=password or 'SenhaTemporaria123',
            )
        
        # Adicionar ao grupo se especificado
        if grupo:
            try:
                group = Group.objects.get(name=grupo)
                user.groups.add(group)
            except Group.DoesNotExist:
                pass
        
        messages.success(request, f'Usuário "{username}" criado com sucesso!')
    
    return redirect('gestao_usuarios')


@admin_required
@require_POST
def deletar_usuario(request, usuario_id):
    """Deleta um usuário."""
    from django.contrib.auth.models import User
    from django.contrib import messages
    
    # Não permitir deletar a si mesmo
    if request.user.id == usuario_id:
        messages.error(request, 'Você não pode deletar sua própria conta!')
        return redirect('gestao_usuarios')
    
    user = get_object_or_404(User, id=usuario_id)
    username = user.username
    user.delete()
    
    messages.success(request, f'Usuário "{username}" deletado com sucesso!')
    return redirect('gestao_usuarios')
