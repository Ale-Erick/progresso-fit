import re

from django.contrib.auth.models import User
from django.db import models
from contas.models import Especialista

# linha no formato "Supino reto 4x10" (nome, séries e repetições)
FORMATO_EXERCICIO = re.compile(r"^(?P<nome>.+?)\s+(?P<series>\d+)\s*[xX×]\s*(?P<reps>\d+(?:-\d+)?)\s*$")


class Treino(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="treinos")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    def exercicios(self):
        # cada linha da descrição vira um exercício; séries e repetições quando no formato "4x10"
        lista = []
        for linha in self.descricao.splitlines():
            linha = linha.strip().lstrip("-• ").strip()
            if not linha:
                continue
            achou = FORMATO_EXERCICIO.match(linha)
            if achou:
                lista.append({"nome": achou["nome"], "series": achou["series"], "reps": achou["reps"]})
            else:
                lista.append({"nome": linha, "series": None, "reps": None})
        return lista


class PlanoAlimentar(models.Model):
    STATUS_CHOICES = (
        ("Pendente", "Pendente"),
        ("Aprovado", "Aprovado"),
        ("Ajustado", "Ajustado"),
        ("Rejeitado", "Rejeitado"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="planos_alimentares")
    especialista = models.ForeignKey(
        Especialista,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planos_revisados",
    )
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pendente")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.status})"