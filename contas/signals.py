from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Perfil


# Signal: o Django chama esta função sempre que um User é salvo.
# Assim todo usuário tem um Perfil, venha ele do cadastro, do admin ou do createsuperuser.
@receiver(post_save, sender=User)
def criar_perfil(sender, instance, created, **kwargs):
    # "created" é True só na primeira vez que o usuário é salvo (na criação)
    if created:
        Perfil.objects.create(
            user=instance,
            nome_completo=instance.get_full_name() or instance.username,
        )
