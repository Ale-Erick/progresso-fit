from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from contas.models import Especialista
from metricas.models import MetricaCorporal
from . import models


OBJETIVOS = [
    "Emagrecimento",
    "Ganho de massa muscular",
    "Manutenção do peso",
    "Desempenho esportivo",
]


def treinos_view(request):
    treinos = models.Treino.objects.select_related("user__perfil").order_by("-created_at")
    return render(request, "planos/treinos.html", {"treinos": treinos})

def nutricao_view(request):
    planos = models.PlanoAlimentar.objects.order_by("-created_at")
    # só especialistas verificados podem revisar planos (RN007)
    especialistas = Especialista.objects.filter(status_verificacao="Verificado").select_related("user__perfil")
    contexto = {"planos": planos, "especialistas": especialistas, "objetivos": OBJETIVOS}
    return render(request, "planos/nutricao.html", contexto)

@require_POST
def solicitar_plano_view(request):
    # UC09: o aluno solicita um plano, que fica pendente até a revisão (RN006)
    if not request.user.is_authenticated:
        messages.error(request, "Entre na sua conta para solicitar um plano alimentar.")
        return redirect("planos:nutricao")

    ultima = MetricaCorporal.objects.filter(user=request.user).order_by("-data", "-created_at").first()
    if ultima is None:
        messages.error(request, "Registre uma medição corporal antes de solicitar um plano alimentar.")
        return redirect("planos:nutricao")

    objetivo = request.POST.get("objetivo", "")
    especialista_id = request.POST.get("especialista", "")
    especialista = None
    if especialista_id.isdigit():
        especialista = Especialista.objects.filter(id=especialista_id, status_verificacao="Verificado").first()
    if objetivo not in OBJETIVOS or especialista is None:
        messages.error(request, "Escolha um objetivo e um especialista verificado.")
        return redirect("planos:nutricao")

    refeicoes = request.POST.get("refeicoes", "")
    restricoes = request.POST.get("restricoes", "").strip()

    # proposta simulada da IA (a integração com a API fica para o RF010)
    linhas = [
        "Proposta gerada automaticamente para revisão do especialista.",
        f"Objetivo: {objetivo}",
        f"Última medição ({ultima.data:%d/%m/%Y}): {ultima.peso} kg, {ultima.altura} m",
    ]
    if ultima.percentual_gordura is not None:
        linhas.append(f"Gordura corporal: {ultima.percentual_gordura}%")
    if refeicoes:
        linhas.append(f"Refeições por dia: {refeicoes}")
    linhas.append(f"Restrições alimentares: {restricoes or 'nenhuma informada'}")

    models.PlanoAlimentar.objects.create(
        user=request.user,
        especialista=especialista,
        titulo=f"Plano alimentar - {objetivo}",
        descricao="\n".join(linhas),
    )
    messages.success(request, f"Plano enviado para revisão de {especialista.nome}. Ele aparecerá aqui como pendente até ser aprovado.")
    return redirect("planos:nutricao")

def validacoes_view(request):
    planos = models.PlanoAlimentar.objects.select_related("user", "especialista__user").order_by("-created_at")
    return render(request, "planos/validacoes.html", {"planos": planos})

def revisar_view(request, plano_id):
    plano = get_object_or_404(models.PlanoAlimentar, id=plano_id)
    # métricas mais recentes do aluno para apoiar a revisão (UC10)
    ultima = MetricaCorporal.objects.filter(user=plano.user).order_by("-data", "-created_at").first()
    contexto = {"plano": plano, "ultima": ultima}
    return render(request, "planos/revisar.html", contexto)
