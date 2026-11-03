from django.contrib import admin
from .models import Treino, PlanoAlimentar


class TreinoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "user", "created_at")
    search_fields = ("titulo",)


class PlanoAlimentarAdmin(admin.ModelAdmin):
    list_display = ("titulo", "user", "status", "especialista")
    search_fields = ("titulo",)
    list_filter = ("status",)


admin.site.register(Treino, TreinoAdmin)
admin.site.register(PlanoAlimentar, PlanoAlimentarAdmin)