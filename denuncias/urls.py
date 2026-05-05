from django.urls import path
from .views import criar_denuncia, sucesso

urlpatterns = [
    path('denuncia/', criar_denuncia, name='criar_denuncia'),
    path('sucesso/', sucesso, name='sucesso'),
]