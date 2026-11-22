from django.urls import path
from . import views

app_name = "planos"

urlpatterns = [
    path("treinos/", views.treinos_view, name="treinos"),
    path("treinos/novo/", views.treino_criar_view, name="treino_criar"),
    path("treinos/<int:treino_id>/editar/", views.treino_editar_view, name="treino_editar"),
    path("treinos/<int:treino_id>/excluir/", views.treino_excluir_view, name="treino_excluir"),
    path("nutricao/", views.nutricao_view, name="nutricao"),
    path("nutricao/solicitar/", views.solicitar_plano_view, name="solicitar_plano"),
    path("validacoes/", views.validacoes_view, name="validacoes"),
    path("validacoes/<int:plano_id>/", views.revisar_view, name="revisar"),
]
