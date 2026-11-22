from django.contrib import admin
from django.utils.html import format_html

from .models import Perfil, Especialista


class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nome_completo", "user", "tipo", "nivel_conhecimento", "publico")
    search_fields = ("nome_completo",)
    list_filter = ("tipo", "nivel_conhecimento")


class EspecialistaAdmin(admin.ModelAdmin):
    """UC11: o administrador analisa o documento e muda o status para Verificado ou Rejeitado."""

    list_display = ("user", "area_atuacao", "registro_profissional", "ver_documento", "status_verificacao", "created_at")
    # list_editable: o status pode ser trocado direto na lista, sem abrir cada pedido
    list_editable = ("status_verificacao",)
    search_fields = ("registro_profissional", "user__email")
    list_filter = ("status_verificacao", "area_atuacao")

    @admin.display(description="Documento")
    def ver_documento(self, especialista):
        # link para abrir o arquivo enviado em outra aba
        if especialista.documento:
            return format_html('<a href="{}" target="_blank">Abrir documento</a>', especialista.documento.url)
        return "-"


admin.site.register(Perfil, PerfilAdmin)
admin.site.register(Especialista, EspecialistaAdmin)
