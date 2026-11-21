from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from . import forms

# aviso exibido nos formulários que ainda não gravam dados (gravação na Etapa 2)
AVISO_DEMONSTRACAO = "Demonstração: os dados ainda não são salvos nesta versão do sistema."


def home_view(request):
    return render(request, "home.html")


def enviar_email_confirmacao(request, user):
    """Manda o e-mail com o link de ativação da conta (RF002)."""
    # uid: o id do usuário codificado para caber na URL
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    # token: código gerado pelo Django para este usuário; expira em PASSWORD_RESET_TIMEOUT (3 dias)
    token = default_token_generator.make_token(user)
    # build_absolute_uri monta o link completo, com http://endereço-do-site
    link = request.build_absolute_uri(reverse("contas:ativar", args=[uid, token]))

    mensagem = render_to_string("contas/email_confirmacao.txt", {"user": user, "link": link})
    # from_email=None usa o DEFAULT_FROM_EMAIL do settings
    send_mail("Confirme seu e-mail - ProgressoFit", mensagem, None, [user.email])


def cadastro_view(request):
    # UC01: cria a conta inativa e envia o e-mail de confirmação
    if request.user.is_authenticated:
        return redirect("contas:perfil")

    if request.method == "POST":
        form = forms.CadastroForm(request.POST)
        if form.is_valid():
            # atomic: o User e o Perfil são gravados juntos; se algo falhar, nada é salvo
            with transaction.atomic():
                user = form.save()
            enviar_email_confirmacao(request, user)
            return redirect("contas:confirmar_email")
        else:
            messages.error(request, "Não foi possível criar a conta. Verifique os campos destacados.")
    else:
        form = forms.CadastroForm()

    return render(request, "contas/cadastro.html", {"form": form})


def confirmar_email_view(request):
    # tela "confira seu e-mail", que também permite pedir um novo link
    if request.method == "POST":
        form = forms.ReenviarConfirmacaoForm(request.POST)
        if form.is_valid():
            # só reenvia para contas que ainda não foram ativadas
            user = User.objects.filter(email__iexact=form.cleaned_data["email"], is_active=False).first()
            if user is not None:
                enviar_email_confirmacao(request, user)
            # mesma resposta tendo ou não conta: assim ninguém descobre quais e-mails estão cadastrados
            messages.success(request, "Se houver uma conta aguardando confirmação com este e-mail, enviamos um novo link.")
            return redirect("contas:confirmar_email")
    else:
        form = forms.ReenviarConfirmacaoForm()

    return render(request, "contas/confirmar_email.html", {"form": form})


def ativar_view(request, uidb64, token):
    # link do e-mail: confere o token e ativa a conta (RF002, diagrama de atividade do cadastro)
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and user.is_active:
        # o link é de uso único: depois de ativada, a conta não é "ativada de novo"
        messages.info(request, "Sua conta já está ativa. É só entrar.")
    elif user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "E-mail confirmado! Agora você já pode entrar.")
    else:
        messages.error(request, "Link de confirmação inválido ou expirado. Peça um novo link abaixo.")
        return redirect("contas:confirmar_email")

    return redirect("login")

def recuperar_senha_view(request):
    enviado = request.method == "POST"
    return render(request, "contas/recuperar_senha.html", {"enviado": enviado})

def perfil_view(request):
    return render(request, "contas/perfil.html")

def perfil_editar_view(request):
    # UC04: após salvar, volta para o perfil
    if request.method == "POST":
        messages.info(request, AVISO_DEMONSTRACAO)
        return redirect("contas:perfil")
    return render(request, "contas/perfil_editar.html")

def verificacao_view(request):
    # UC05: a solicitação fica pendente de verificação pelo administrador
    if request.method == "POST":
        messages.info(request, f"Solicitação de verificação enviada para análise. {AVISO_DEMONSTRACAO}")
        return redirect("contas:perfil")
    return render(request, "contas/verificacao.html")
