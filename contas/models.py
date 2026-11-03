from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
    NIVEL_CHOICES = (
        ("Iniciante", "Iniciante"),
        ("Intermediário", "Intermediário"),
        ("Avançado", "Avançado"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    nome_completo = models.CharField(max_length=150)
    descricao = models.CharField(max_length=150, blank=True)
    publico = models.BooleanField(default=False)
    nivel_conhecimento = models.CharField(
        max_length=20, choices=NIVEL_CHOICES, default="Iniciante"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_completo


class Especialista(models.Model):
    AREA_CHOICES = (
        ("Nutricionista", "Nutricionista"),
        ("Educador fisico", "Educador físico"),
        ("Médico do esporte", "Médico do esporte"),
    )
    STATUS_CHOICES = (
        ("Pendente", "Pendente de verificação"),
        ("Verificado", "Verificado"),
        ("Rejeitado", "Rejeitado"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="especialista")
    area_atuacao = models.CharField(max_length=30, choices=AREA_CHOICES)
    registro_profissional = models.CharField(max_length=50, unique=True)
    status_verificacao = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="Pendente"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.area_atuacao}"

    @property
    def nome(self):
        # nome de exibição: perfil, depois nome do usuário, depois username
        perfil = getattr(self.user, "perfil", None)
        if perfil and perfil.nome_completo:
            return perfil.nome_completo
        return self.user.get_full_name() or self.user.username