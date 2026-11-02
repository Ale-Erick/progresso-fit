from django.shortcuts import render, redirect

# Create your views here.
def home_view(request):
    return render(request, "home.html")

def login_view(request):
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
    return render(request, "contas/perfil_editar.html")

def verificacao_view(request):
    return render(request, "contas/verificacao.html")
