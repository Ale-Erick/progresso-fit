from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from contas.views import AVISO_DEMONSTRACAO
from . import models


# circunferências (campo, rótulo) agrupadas por região do corpo
CIRCUNFERENCIAS = [
    ("Membros superiores", [
        ("peitoral", "Peitoral"),
        ("braco_esq", "Braço esquerdo"),
        ("braco_dir", "Braço direito"),
    ]),
    ("Tronco / cintura", [
        ("cintura", "Cintura"),
        ("abdomen", "Abdômen"),
        ("quadril", "Quadril"),
    ]),
    ("Membros inferiores", [
        ("coxa_esq", "Coxa esquerda"),
        ("coxa_dir", "Coxa direita"),
        ("panturrilha_esq", "Panturrilha esquerda"),
        ("panturrilha_dir", "Panturrilha direita"),
    ]),
]


def registrar_view(request):
    # UC03: após registrar, o aluno é levado à tela de evolução
    if request.method == "POST":
        messages.info(request, AVISO_DEMONSTRACAO)
        return redirect("metricas:evolucao")
    hoje = timezone.localdate()
    contexto = {"hoje": hoje, "circunferencias": CIRCUNFERENCIAS}
    return render(request, "metricas/registrar.html", contexto)

def evolucao_view(request):
    metricas = models.MetricaCorporal.objects.order_by("-data", "-created_at")
    ultima = metricas.first()

    massa_magra = None
    if ultima and ultima.percentual_gordura is not None:
        massa_magra = round(ultima.peso * (100 - ultima.percentual_gordura) / 100, 1)

    # dados do gráfico em ordem cronológica
    cronologica = list(metricas)[::-1]
    grafico = {
        "datas": [m.data.strftime("%d/%m/%Y") for m in cronologica],
        "peso": [float(m.peso) for m in cronologica],
        "gordura": [
            float(m.percentual_gordura) if m.percentual_gordura is not None else None
            for m in cronologica
        ],
    }

    contexto = {
        "metricas": metricas,
        "ultima": ultima,
        "massa_magra": massa_magra,
        "grafico": grafico,
    }
    return render(request, "metricas/lista.html", contexto)

def detalhe_view(request, metrica_id):
    metrica = get_object_or_404(models.MetricaCorporal, id=metrica_id)
    # valores de cada circunferência para exibir agrupados
    circunferencias = [
        (grupo, [(rotulo, getattr(metrica, campo)) for campo, rotulo in campos])
        for grupo, campos in CIRCUNFERENCIAS
    ]
    contexto = {"metrica": metrica, "circunferencias": circunferencias}
    return render(request, "metricas/detalhe.html", contexto)
