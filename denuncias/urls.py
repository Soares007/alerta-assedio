from django.urls import path
from .views import home, criar_denuncia, sucesso, minhas_denuncias, dashboard, todas_denuncias

urlpatterns = [
    path('', home, name='home'),
    path('denuncia/', criar_denuncia, name='criar_denuncia'),
    path('sucesso/', sucesso, name='sucesso'),
    path('minhas-denuncias/', minhas_denuncias,  name='minhas_denuncias'),
    path('dashboard/', dashboard, name='dashboard'),
    path('todas-denuncias/', todas_denuncias, name='todas_denuncias'),
]