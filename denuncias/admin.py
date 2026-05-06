from django.contrib import admin
from .models import Denuncia

@admin.register(Denuncia)
class DenunciaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'status', 'anonima', 'usuario', 'data_criacao')
    list_filter = ('tipo', 'status', 'anonima', 'data_criacao')
    search_fields = ('descricao', 'usuario_username')
    ordering = ('-data_criacao',)
    readonly_fields = ('data_criacao',)

    fieldsets = (
        ('Informações da denúncia', {
            'fields': ('tipo', 'descricao', 'anonima')
        }),
        ('Usuário e status',
         {
             'fields': ('usuario', 'status')
         }),
        ('Resposta RH', {
             'fields': ('resposta_rh',)
         }),
         ('Datas', {
             'fields': ('data_criacao',)
         }),
    )
