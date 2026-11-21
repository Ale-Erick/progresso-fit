from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.forms import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import forms, models


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


def medicoes_do_usuario(user):
    # RN008: cada aluno só enxerga as próprias medições
    return models.MetricaCorporal.objects.filter(user=user).order_by("-data", "-created_at")


@login_required
def registrar_view(request):
    # UC03: registra a medição do aluno logado e leva à tela de evolução
    if request.method == "POST":
        form = forms.MetricaForm(request.POST)
        if form.is_valid():
            # commit=False: monta o objeto sem salvar, para preencher o usuário antes
            metrica = form.save(commit=False)
            metrica.user = request.user
            metrica.save()
            messages.success(request, "Medição registrada com sucesso!")
            return redirect("metricas:evolucao")
        else:
            messages.error(request, "Não foi possível salvar a medição. Verifique os campos destacados.")
    else:
        # UC03, passo 2: o formulário já vem com os valores da última medição
        inicial = {}
        ultima = medicoes_do_usuario(request.user).first()
        if ultima:
            # model_to_dict transforma o objeto em um dicionário {campo: valor}
            inicial = model_to_dict(ultima, exclude=["id", "user", "data"])
        # data de hoje no formato do <input type="date"> (AAAA-MM-DD)
        inicial["data"] = timezone.localdate().isoformat()
        form = forms.MetricaForm(initial=inicial)

    # cada circunferência vira o campo do form (form[campo]), para o template mostrar valor e erros
    circunferencias = [
        (grupo, [(form[campo], rotulo) for campo, rotulo in campos])
        for grupo, campos in CIRCUNFERENCIAS
    ]
    contexto = {"form": form, "circunferencias": circunferencias}
    return render(request, "metricas/registrar.html", contexto)


@login_required
def evolucao_view(request):
    metricas = medicoes_do_usuario(request.user)
    ultima = metricas.first()

    massa_magra = None
    if ultima and ultima.percentual_gordura is not None:
        massa_magra = round(ultima.peso * (100 - ultima.percentual_gordura) / 100, 1)

    # dados do gráfico em ordem cronológica (o gráfico usa todas as medições)
    cronologica = list(metricas)[::-1]
    grafico = {
        "datas": [m.data.strftime("%d/%m/%Y") for m in cronologica],
        "peso": [float(m.peso) for m in cronologica],
        "gordura": [
            float(m.percentual_gordura) if m.percentual_gordura is not None else None
            for m in cronologica
        ],
    }

    # histórico paginado: 10 medições por página (?page=2, ?page=3...)
    paginator = Paginator(metricas, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    # UC06, passo 3: o nível de conhecimento corporal fica no perfil
    perfil = getattr(request.user, "perfil", None)

    contexto = {
        "page_obj": page_obj,
        "ultima": ultima,
        "massa_magra": massa_magra,
        "grafico": grafico,
        "nivel": perfil.nivel_conhecimento if perfil else None,
    }
    return render(request, "metricas/lista.html", contexto)


@login_required
def detalhe_view(request, metrica_id):
    # user=request.user: a medição de outro aluno responde 404 (RN008)
    metrica = get_object_or_404(models.MetricaCorporal, id=metrica_id, user=request.user)
    # valores de cada circunferência para exibir agrupados
    circunferencias = [
        (grupo, [(rotulo, getattr(metrica, campo)) for campo, rotulo in campos])
        for grupo, campos in CIRCUNFERENCIAS
    ]
    contexto = {"metrica": metrica, "circunferencias": circunferencias}
    return render(request, "metricas/detalhe.html", contexto)


@login_required
@require_POST
def excluir_view(request, metrica_id):
    # só exclui por POST (botão do modal de confirmação). Não existe edição:
    # pelo RN004 a medição é imutável, mas pode ser removida se foi lançada por engano.
    metrica = get_object_or_404(models.MetricaCorporal, id=metrica_id, user=request.user)
    metrica.delete()
    messages.success(request, "Medição excluída.")
    return redirect("metricas:evolucao")
