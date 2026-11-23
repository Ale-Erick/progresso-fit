from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


# ---------- Quem é o usuário? ----------

def eh_aluno(user):
    perfil = getattr(user, "perfil", None)
    return perfil is not None and perfil.tipo == "Aluno"


def eh_especialista(user):
    perfil = getattr(user, "perfil", None)
    return perfil is not None and perfil.tipo == "Especialista"


def eh_especialista_verificado(user):
    # RN007: só o especialista aprovado pelo administrador pode revisar planos
    especialista = getattr(user, "especialista", None)  # None se ainda não enviou a verificação
    return eh_especialista(user) and especialista is not None and especialista.status_verificacao == "Verificado"


# ---------- Decorators para proteger as views ----------
# Funcionam como o @login_required, mas também conferem o tipo de conta.
# Quem não está logado vai para o login; quem é do tipo errado volta para o Início
# com um aviso, em vez de ver uma tela de erro.

def aluno_required(view):
    @wraps(view)  # mantém o nome e a documentação da view original
    @login_required
    def view_protegida(request, *args, **kwargs):
        if not eh_aluno(request.user):
            messages.warning(request, "Esta área é exclusiva para alunos.")
            return redirect("contas:home")
        return view(request, *args, **kwargs)
    return view_protegida


def especialista_required(view):
    @wraps(view)
    @login_required
    def view_protegida(request, *args, **kwargs):
        if not eh_especialista(request.user):
            messages.warning(request, "Esta área é exclusiva para especialistas.")
            return redirect("contas:home")
        return view(request, *args, **kwargs)
    return view_protegida


def especialista_verificado_required(view):
    # UC10, exceção 0a: especialista sem verificação aprovada é bloqueado com uma mensagem
    @wraps(view)
    @especialista_required  # primeiro confere login e tipo de conta
    def view_protegida(request, *args, **kwargs):
        if not eh_especialista_verificado(request.user):
            messages.warning(request, "O painel de validações só é liberado depois que o administrador verificar seu registro profissional.")
            return redirect("contas:verificacao")
        return view(request, *args, **kwargs)
    return view_protegida
