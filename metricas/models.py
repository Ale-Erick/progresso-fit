from django.contrib.auth.models import User
from django.db import models


class MetricaCorporal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="metricas")
    data = models.DateField()
    peso = models.DecimalField(max_digits=5, decimal_places=2)  # kg (obrigatório)
    altura = models.DecimalField(max_digits=3, decimal_places=2)  # m (obrigatório)
    percentual_gordura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)
    gordura_visceral = models.IntegerField(blank=True, null=True)
    metabolismo_basal = models.IntegerField(blank=True, null=True)  # kcal

    # Circunferências em cm (opcionais)
    # Membros superiores
    peitoral = models.FloatField(blank=True, null=True)
    braco_esq = models.FloatField(blank=True, null=True)
    braco_dir = models.FloatField(blank=True, null=True)

    # Tronco / cintura
    cintura = models.FloatField(blank=True, null=True)
    abdomen = models.FloatField(blank=True, null=True)
    quadril = models.FloatField(blank=True, null=True)

    # Membros inferiores
    coxa_esq = models.FloatField(blank=True, null=True)
    coxa_dir = models.FloatField(blank=True, null=True)
    panturrilha_esq = models.FloatField(blank=True, null=True)
    panturrilha_dir = models.FloatField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.data} - {self.peso} kg"
