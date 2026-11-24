from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from contas.models import Especialista
from contas.permissoes import aluno_required, especialista_verificado_required
from metricas.models import MetricaCorporal
from . import forms, models


OBJETIVOS = [
    "Emagrecimento",
    "Ganho de massa muscular",
    "Manutenção do peso",
    "Desempenho esportivo",
]


@aluno_required
def treinos_view(request):
    # RN008: o aluno só vê as próprias fichas de treino
    treinos = models.Treino.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "planos/treinos.html", {"treinos": treinos})

@aluno_required
def treino_criar_view(request):
    if request.method == "POST":
        form = forms.TreinoForm(request.POST)
        if form.is_valid():
            # commit=False: preenche o dono do treino antes de salvar
            treino = form.save(commit=False)
            treino.user = request.user
            treino.save()
            messages.success(request, "Treino criado com sucesso!")
            return redirect("planos:treinos")
        else:
            messages.error(request, "Não foi possível salvar o treino. Verifique os campos destacados.")
    else:
        form = forms.TreinoForm()

    return render(request, "planos/treino_form.html", {"form": form})

@aluno_required
def treino_editar_view(request, treino_id):
    # user=request.user: o aluno só edita os próprios treinos; o de outro dá 404 (RN008)
    treino = get_object_or_404(models.Treino, id=treino_id, user=request.user)

    if request.method == "POST":
        form = forms.TreinoForm(request.POST, instance=treino)
        if form.is_valid():
            form.save()
            messages.success(request, "Treino atualizado com sucesso!")
            return redirect("planos:treinos")
        else:
            messages.error(request, "Não foi possível salvar o treino. Verifique os campos destacados.")
    else:
        form = forms.TreinoForm(instance=treino)

    # o mesmo template do criar; com "treino" no contexto ele mostra "Editar" e o botão de excluir
    return render(request, "planos/treino_form.html", {"form": form, "treino": treino})

@aluno_required
@require_POST
def treino_excluir_view(request, treino_id):
    # só exclui por POST (botão do modal de confirmação)
    treino = get_object_or_404(models.Treino, id=treino_id, user=request.user)
    treino.delete()
    messages.success(request, f"Treino \"{treino.titulo}\" excluído.")
    return redirect("planos:treinos")

@aluno_required
def nutricao_view(request):
    # RN008: o aluno só vê os próprios planos alimentares
    planos = models.PlanoAlimentar.objects.filter(user=request.user).order_by("-created_at")
    # só especialistas verificados podem revisar planos (RN007)
    especialistas = Especialista.objects.filter(status_verificacao="Verificado").select_related("user__perfil")
    contexto = {"planos": planos, "especialistas": especialistas, "objetivos": OBJETIVOS}
    return render(request, "planos/nutricao.html", contexto)

@aluno_required
@require_POST
def solicitar_plano_view(request):
    # UC09: o aluno solicita um plano, que fica pendente até a revisão (RN006)
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

# filtros do painel: (valor do ?status=, texto da aba)
FILTROS_STATUS = [
    ("Pendente", "Pendentes"),
    ("Aprovado", "Aprovados"),
    ("Ajustado", "Ajustados"),
    ("Rejeitado", "Rejeitados"),
    ("Todos", "Todos"),
]

@especialista_verificado_required
def validacoes_view(request):
    # UC10, passo 2: só os planos enviados para o especialista logado (RN008)
    planos = models.PlanoAlimentar.objects.filter(especialista=request.user.especialista)

    # filtro por status pela URL (?status=Aprovado); sem filtro, mostra os pendentes
    status = request.GET.get("status", "Pendente")
    if status != "Todos":
        planos = planos.filter(status=status)
    planos = planos.select_related("user__perfil").order_by("-created_at")

    paginator = Paginator(planos, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    contexto = {"page_obj": page_obj, "status": status, "filtros": FILTROS_STATUS}
    return render(request, "planos/validacoes.html", contexto)

@especialista_verificado_required
def revisar_view(request, plano_id):
    # o especialista só abre os planos enviados para ele; o de outro especialista dá 404 (RN008)
    plano = get_object_or_404(models.PlanoAlimentar, id=plano_id, especialista=request.user.especialista)
    # métricas mais recentes do aluno para apoiar a revisão (UC10, passo 3)
    ultima = MetricaCorporal.objects.filter(user=plano.user).order_by("-data", "-created_at").first()
    pendente = plano.status == "Pendente"

    if request.method == "POST":
        if not pendente:
            messages.warning(request, "Este plano já foi revisado.")
            return redirect("planos:revisar", plano_id=plano.id)
        form = forms.RevisaoForm(request.POST)
        if form.is_valid():
            decisao = form.cleaned_data["decisao"]
            # UC10, passo 5: a decisão vira o status; Aprovado/Ajustado liberam o plano para o aluno (RN006)
            plano.status = decisao
            if decisao == "Ajustado":
                plano.descricao = form.cleaned_data["descricao_ajustada"]
            plano.observacao = form.cleaned_data["observacao"]
            plano.revisado_em = timezone.now()
            plano.save()
            messages.success(request, f"Revisão salva: plano {decisao.lower()}.")
            return redirect("planos:validacoes")
        else:
            messages.error(request, "Não foi possível salvar a revisão. Verifique os campos destacados.")
    else:
        # o plano já revisado abre só para leitura (sem formulário)
        form = forms.RevisaoForm(initial={"descricao_ajustada": plano.descricao}) if pendente else None

    contexto = {"plano": plano, "ultima": ultima, "form": form}
    return render(request, "planos/revisar.html", contexto)
