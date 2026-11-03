from django.contrib import admin 
from .models import MetricaCorporal 

class MetricaCorporalAdmin(admin.ModelAdmin):    
    list_display = ("user", "data", "peso", "altura", "percentual_gordura")    
    search_fields = ("user__username",)    
    list_filter = ("data",) 

admin.site.register(MetricaCorporal, MetricaCorporalAdmin)