from django.urls import path 
from . import views

app_name = "metricas" 

urlpatterns = [ 
    path("registrar/", views.registrar_view, name="registrar"),
    path("evolucao/", views.evolucao_view, name="evolucao"),  
    path("detalhe/<int:metrica_id>/", views.detalhe_view, name="detalhe"),
        ]