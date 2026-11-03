from django.contrib import admin
from .models import Perfil, Especialista


class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nome_completo", "user", "nivel_conhecimento", "publico")
    search_fields = ("nome_completo",)
    list_filter = ("nivel_conhecimento",)


class EspecialistaAdmin(admin.ModelAdmin):
    list_display = ("user", "area_atuacao", "registro_profissional", "status_verificacao")
    search_fields = ("registro_profissional",)
    list_filter = ("area_atuacao", "status_verificacao")


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Especialista, EspecialistaAdmin)