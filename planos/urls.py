from django.urls import path
from . import views

app_name = "planos"

urlpatterns = [
    path("treinos/", views.treinos_view, name="treinos"),
    path("nutricao/", views.nutricao_view, name="nutricao"),
    path("nutricao/solicitar/", views.solicitar_plano_view, name="solicitar_plano"),
    path("validacoes/", views.validacoes_view, name="validacoes"),
    path("validacoes/<int:plano_id>/", views.revisar_view, name="revisar"),
]
