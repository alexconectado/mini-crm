"""
Decoradores e utilitários de permissão para o Mini-CRM
"""

from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def grupo_required(*grupos):
    """
    Decorador que valida se o usuário pertence a um dos grupos especificados.
    Uso: @grupo_required('Admin', 'Comercial')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url='login')
        def wrapper(request, *args, **kwargs):
            # Superuser tem acesso a tudo
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Verificar se o usuário está em um dos grupos requeridos
            user_grupos = request.user.groups.values_list('name', flat=True)
            
            if any(grupo in user_grupos for grupo in grupos):
                return view_func(request, *args, **kwargs)
            
            # Acesso negado - redirecionar para kanban
            return redirect('kanban')
        
        return wrapper
    return decorator


def comercial_required(view_func):
    """Decorador para permitir apenas Comercial e Admin"""
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        user_grupos = request.user.groups.values_list('name', flat=True)
        if 'Comercial' in user_grupos or 'Admin' in user_grupos:
            return view_func(request, *args, **kwargs)
        
        return redirect('login')
    
    return wrapper


def admin_required(view_func):
    """Decorador para permitir apenas Admin"""
    @wraps(view_func)
    @login_required(login_url='login')
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        user_grupos = request.user.groups.values_list('name', flat=True)
        if 'Admin' in user_grupos:
            return view_func(request, *args, **kwargs)
        
        return redirect('login')
    
    return wrapper


def api_login_required(view_func):
    """
    Decorador para APIs que retorna JSON em caso de erro de autenticação.
    Evita que requisições AJAX recebam HTML de redirecionamento.
    """
    from django.http import JsonResponse
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Autenticação necessária. Por favor, faça login.'},
                status=401
            )
        return view_func(request, *args, **kwargs)
    
    return wrapper


def api_comercial_required(view_func):
    """
    Decorador para APIs que retorna JSON em caso de erro de autenticação/permissão.
    Permite apenas usuários do grupo Comercial ou Admin.
    """
    from django.http import JsonResponse
    
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Autenticação necessária. Por favor, faça login.'},
                status=401
            )
        
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        user_grupos = request.user.groups.values_list('name', flat=True)
        if 'Comercial' in user_grupos or 'Admin' in user_grupos:
            return view_func(request, *args, **kwargs)
        
        return JsonResponse(
            {'error': 'Sem permissão para acessar este recurso.'},
            status=403
        )
    
    return wrapper
