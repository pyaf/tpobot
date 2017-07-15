from django.contrib import admin
from .models import Company, Sucker

class CompanyAdmin(admin.ModelAdmin):


    list_max_show_all = 500
    list_display = ('company_name', 'modified_date', 'purpose')
    ordering = ('modified_date',)
    search_fields = ('company_name',)

admin.site.register(Company, CompanyAdmin)

admin.site.register(Sucker)
