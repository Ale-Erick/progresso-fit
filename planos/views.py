from django.shortcuts import render, get_object_or_404
from metricas.models import MetricaCorporal
from . import models


def treinos_view(request):
    treinos = models.Treino.objects.all()
    return render(request, "planos/treinos.html", {"treinos": treinos})

def nutricao_view(request):
    planos = models.PlanoAlimentar.objects.all()
    return render(request, "planos/nutricao.html", {"planos": planos})

def validacoes_view(request):
    planos = models.PlanoAlimentar.objects.all()
    return render(request, "planos/validacoes.html", {"planos": planos})

def revisar_view(request, plano_id):
    plano = get_object_or_404(models.PlanoAlimentar, id=plano_id)
    # métricas mais recentes do aluno para apoiar a revisão (UC10)
    ultima = MetricaCorporal.objects.filter(user=plano.user).order_by("-data", "-created_at").first()
    contexto = {"plano": plano, "ultima": ultima}
    return render(request, "planos/revisar.html", contexto)
