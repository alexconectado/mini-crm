"""
Script para criar grupos e permissões no Mini-CRM.
Execute com: python manage.py shell < setup_grupos.py
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from crm.models import RegistroComercial, ContatoHistorico

# Criar grupo Comercial
grupo_comercial, created = Group.objects.get_or_create(name='Comercial')
if created:
    print("✓ Grupo 'Comercial' criado")
else:
    print("✓ Grupo 'Comercial' já existia")

# Criar grupo Admin
grupo_admin, created = Group.objects.get_or_create(name='Admin')
if created:
    print("✓ Grupo 'Admin' criado")
else:
    print("✓ Grupo 'Admin' já existia")

# Limpar permissões anteriores
grupo_comercial.permissions.clear()
grupo_admin.permissions.clear()

# Obter permissões da app CRM
ct_registro = ContentType.objects.get_for_model(RegistroComercial)
ct_contato = ContentType.objects.get_for_model(ContatoHistorico)

# Permissões do grupo Comercial (Kanban + Métricas)
perms_comercial = [
    'view_registrocomercial',  # Ver registros
    'add_registrocomercial',   # Adicionar registros
    'change_registrocomercial', # Editar registros
    'view_contatohistorico',   # Ver histórico de contatos
    'add_contatohistorico',    # Adicionar contatos
]

for perm_codename in perms_comercial:
    try:
        perm = Permission.objects.get(content_type=ct_registro, codename=perm_codename)
        grupo_comercial.permissions.add(perm)
    except Permission.DoesNotExist:
        print(f"⚠ Permissão '{perm_codename}' não encontrada")

print("✓ Permissões do grupo 'Comercial' configuradas")

# Permissões do grupo Admin (Tudo)
perms_admin = Permission.objects.filter(
    content_type__in=[ct_registro, ct_contato]
)

grupo_admin.permissions.set(perms_admin)
print("✓ Permissões do grupo 'Admin' configuradas")

print("\n✅ Setup concluído!")
print("\nGrupos criados:")
print("  - Comercial: Acesso apenas a Kanban e Métricas")
print("  - Admin: Acesso completo (Kanban, Métricas, Importar, Admin)")
print("\nPróximo passo: Adicionar usuários aos grupos no admin do Django")
