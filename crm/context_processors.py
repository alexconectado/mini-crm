"""
Context Processors para Mini-CRM
"""

def menu_permissions(request):
    """Adiciona informações de permissão ao contexto de template."""
    if not request.user.is_authenticated:
        return {}
    
    user_groups = list(request.user.groups.values_list('name', flat=True))
    
    return {
        'is_admin_user': request.user.is_superuser or 'Admin' in user_groups,
        'is_comercial_user': 'Comercial' in user_groups or 'Admin' in user_groups or request.user.is_superuser,
        'user_groups': user_groups,
    }
