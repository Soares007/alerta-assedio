from django.urls import path
from .views import criar_denuncia, sucesso, minhas_denuncias

urlpatterns = [
    path('denuncia/', criar_denuncia, name='criar_denuncia'),
    path('sucesso/', sucesso, name='sucesso'),
    path('minhas-denuncias/', minhas_denuncias,  name='minhas_denuncias'),
]