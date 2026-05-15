from django.contrib import admin
from .models import Denuncia, Notificacao, Setor, AnexoDenuncia, PerfilUsuario
from .models import FeedbackIA

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
    
@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'lida', 'data_criacao')
    list_filter = ('lida', 'data_criacao')
    search_fields = ('titulo', 'mensagem', 'usuario_username')

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'setor')
    search_fields = ('usuario__username', 'setor__nome')


@admin.register(AnexoDenuncia)
class AnexoDenunciaAdmin(admin.ModelAdmin):
    list_display = ('denuncia', 'arquivo', 'link', 'data_envio')
    search_fields = ('link',)
    
@admin.register(FeedbackIA)
class FeedbackIAAdmin(admin.ModelAdmin):
    list_display = ('tipo_sugerido', 'tipo_correto', 'usuario', 'data_criacao')
    list_filter = ('tipo_sugerido', 'tipo_correto', 'data_criacao')
    search_fields = ('texto',)
