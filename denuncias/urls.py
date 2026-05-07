from django.urls import path
from .views import home, criar_denuncia, sucesso, minhas_denuncias, dashboard, todas_denuncias, painel_rh, marcar_notificacoes_lidas, api_notificacoes

urlpatterns = [
    path('', home, name='home'),
    path('denuncia/', criar_denuncia, name='criar_denuncia'),
    path('sucesso/', sucesso, name='sucesso'),
    path('minhas-denuncias/', minhas_denuncias,  name='minhas_denuncias'),
    path('dashboard/', dashboard, name='dashboard'),
    path('todas-denuncias/', todas_denuncias, name='todas_denuncias'),
    path('painel-rh/', painel_rh, name='painel_rh'),
    path('painel-rh/<int:denuncia_id>/', painel_rh, name='painel_rh_detalhe'),
    path('notificacoes/marcar-lidas/', marcar_notificacoes_lidas, name='marcar_notificacoes_lidas'),
    path('api/notificacoes/', api_notificacoes, name='api_notificacoes'),
]