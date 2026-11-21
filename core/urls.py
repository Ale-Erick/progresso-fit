"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

from contas.forms import LoginForm

urlpatterns = [
    path("admin/", admin.site.urls),
    # Login do Django usando o nosso formulário (e-mail no lugar do usuário).
    # Fica antes do include abaixo para "accounts/login/" usar esta versão.
    # redirect_authenticated_user: quem já está logado não vê a tela de login de novo.
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True),
        name="login",
    ),
    # Rotas prontas do Django: logout, password_reset, password_change etc.
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("contas.urls")),
    path("metricas/", include("metricas.urls")),
    path("planos/", include("planos.urls")),
    ]

# Em desenvolvimento (DEBUG = True), o próprio Django entrega os arquivos de /media/
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
