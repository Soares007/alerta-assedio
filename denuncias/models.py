from django.db import models
from django.contrib.auth.models import User

class Denuncia(models.Model):
    TIPOS = [
        ('moral', 'Assédio Moral'),
        ('sexual', 'Assédio Sexual'),
        ('abuso', 'Abuso de Poder'),
    ]

    STATUS = [
        ('recebida', 'Recebida'),
        ('analise', 'Em análise'),
        ('resolvida', 'Resolvida'),
    ]

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    descricao = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS)
    anonima = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default='recebida')
    data_criacao = models.DateTimeField(auto_now_add=True)
    resposta_rh = models.TextField(blank=True, null=True)

    def _str_(self):
        return f"{self.get_tipo_display()} - {self.get_status_display()}"
    
class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    
    def _str_(self):
        return self.titulo

