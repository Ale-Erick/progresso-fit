from django.contrib import messages
from django.shortcuts import render, redirect

# aviso exibido nos formulários que ainda não gravam dados (gravação na Etapa 2)
AVISO_DEMONSTRACAO = "Demonstração: os dados ainda não são salvos nesta versão do sistema."


def home_view(request):
    return render(request, "home.html")

def login_view(request):
    # UC02: após entrar, o usuário é levado ao perfil
    if request.method == "POST":
        messages.info(request, AVISO_DEMONSTRACAO)
        return redirect("contas:perfil")
    return render(request, "contas/login.html")

def cadastro_view(request):
    # após o envio, o usuário é levado ao aviso de confirmação de e-mail (UC01)
    if request.method == "POST":
        return redirect("contas:confirmar_email")
    return render(request, "contas/cadastro.html")

def confirmar_email_view(request):
    return render(request, "contas/confirmar_email.html")

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
