from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group


@receiver(post_save, sender=User)
def add_user_to_comercial_group(sender, instance, created, **kwargs):
    """
    Automaticamente adiciona usuários criados ao grupo 'Comercial'
    (exceto superusers que não devem estar no grupo)
    """
    if created and not instance.is_superuser:
        try:
            comercial_group = Group.objects.get(name='Comercial')
            instance.groups.add(comercial_group)
        except Group.DoesNotExist:
            # Se o grupo não existir, será criado automaticamente na primeira migração
            pass
