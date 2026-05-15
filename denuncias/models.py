from django.db import models
from django.contrib.auth.models import User


class Setor(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.usuario.username


class Denuncia(models.Model):
    TIPOS = [
    ('moral', 'Assédio Moral'),
    ('sexual', 'Assédio Sexual'),
    ('abuso', 'Abuso de Poder'),
    ('discriminacao', 'Discriminação'),
    ('ameaca', 'Ameaça'),
    ('violencia', 'Violência'),
    ('outros', 'Outros'),
    ]

    STATUS = [
        ("recebida", "Recebida"),
        ("analise", "Em análise"),
        ("resolvida", "Resolvida"),
    ]
    
    GRAVIDADES = [
    ('baixa', 'Baixa'),
    ('media', 'Média'),
    ('alta', 'Alta'),
    ('critica', 'Crítica'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.TextField()
    resumo_ia = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    anonima = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default="recebida")
    prioridade_ia = models.IntegerField(default=1)
    gravidade = models.CharField(
    max_length=20,
    choices=GRAVIDADES,
    default='baixa')
    urgente = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)
    resposta_rh = models.TextField(blank=True, null=True)
    setor = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True)
    exibir_setor = models.BooleanField(default=True)
    link_anexo = models.URLField(blank=True, null=True)

    def _str_(self):
        return f"{self.get_tipo_display()} - {self.get_status_display()}"


class AnexoDenuncia(models.Model):
    denuncia = models.ForeignKey(
        Denuncia, on_delete=models.CASCADE, related_name="anexos"
    )
    arquivo = models.FileField(upload_to="anexos_denuncias/", blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anexo da denúncia {self.denuncia.id}"


class Notificacao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    mensagem = models.TextField()
    lida = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return self.titulo
    
class FeedbackIA(models.Model):
    texto = models.TextField()
    tipo_sugerido = models.CharField(max_length=50)
    tipo_correto = models.CharField(max_length=50)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_sugerido} -> {self.tipo_correto}"
