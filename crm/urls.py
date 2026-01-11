from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_config

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.kanban_view, name='kanban'),
    path('criar-registro/', views.criar_registro, name='criar_registro'),
    path('mover-kanban/<uuid:registro_id>/', views.mover_para_kanban, name='mover_para_kanban'),
    path('mover-backlog/<uuid:registro_id>/', views.mover_para_backlog, name='mover_para_backlog'),
    path('atualizar-status/<uuid:registro_id>/', views.atualizar_status, name='atualizar_status'),
    path('registrar-contato/<uuid:registro_id>/', views.registrar_contato, name='registrar_contato'),
    path('registrar-contato-htmx/<uuid:registro_id>/', views.registrar_contato_htmx, name='registrar_contato_htmx'),
    path('metricas/', views.metricas_view, name='metricas'),
    path('meu-desempenho/', views.meu_desempenho, name='meu_desempenho'),
    path('importar-csv/', views.importar_csv_view, name='importar_csv'),
    path('gestao-usuarios/', views.gestao_usuarios, name='gestao_usuarios'),
    path('api/desempenho-vendedor/<int:vendedor_id>/', views.desempenho_vendedor_api, name='desempenho_vendedor_api'),
    path('api/carregar-mais-registros/', views.carregar_mais_registros_api, name='carregar_mais_registros'),
    
    # Configuração do funil (admin only)
    path('admin/configuracao-funil/', views_config.configuracao_funil, name='configuracao_funil'),
    path('api/admin/toggle-resultado-ativo/<int:resultado_id>/', views_config.toggle_resultado_ativo, name='toggle_resultado_ativo'),
    path('api/admin/toggle-passo-ativo/<int:passo_id>/', views_config.toggle_passo_ativo, name='toggle_passo_ativo'),
    path('arquivados/', views.arquivados_view, name='arquivados'),
    path('contas-ativas/', views.contas_ativas_view, name='contas_ativas'),
    path('restaurar/<uuid:registro_id>/', views.restaurar_lead, name='restaurar_lead'),
    path('criar-usuario/', views.criar_usuario, name='criar_usuario'),
    path('deletar-usuario/<int:usuario_id>/', views.deletar_usuario, name='deletar_usuario'),
]
