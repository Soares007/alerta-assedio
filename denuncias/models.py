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
    tipo = models.CharField(max_length=20, choices=TIPOS)
    anonima = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS, default="recebida")
    gravidade = models.CharField(
    max_length=20,
    choices=GRAVIDADES,
    default='baixa'
)
    urgente = models.BooleanField(default=False)
    prioridade_ia = models.IntegerField(default=1)
    resumo_ia = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    arquivada = models.BooleanField(default=False)
    data_arquivamento = models.DateTimeField(null=True, blank=True)
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
    STATUS_LINK = [
    ('seguro', 'Aparentemente seguro'),
    ('suspeito', 'Suspeito'),
    ('perigoso', 'Potencialmente perigoso'),
]
    status_link = models.CharField(
        max_length=20,
        choices=STATUS_LINK,
        blank=True,
        null=True
    )
    motivo_status_link = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Anexo da denúncia {self.denuncia.id}"
    
    motivo_link = models.TextField(blank=True, null=True)   


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
    
class ChatDenuncia(models.Model):
    denuncia = models.OneToOneField(
        Denuncia,
        on_delete=models.CASCADE,
        related_name='chat'
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Chat da denúncia #{self.denuncia.id}"


class MensagemChatDenuncia(models.Model):
    TIPOS_AUTOR = [
        ('funcionario', 'Funcionário'),
        ('rh', 'RH'),
        ('ia', 'IA'),
        ('sistema', 'Sistema'),
    ]

    chat = models.ForeignKey(
        ChatDenuncia,
        on_delete=models.CASCADE,
        related_name='mensagens'
    )

    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    tipo_autor = models.CharField(
        max_length=20,
        choices=TIPOS_AUTOR
    )

    mensagem = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)

    anonimo = models.BooleanField(default=False)
    
    link_detectado = models.URLField(blank=True, null=True)
    
    status_link = models.CharField(
        max_length=20,
         choices=[
            ('seguro', 'Aparentemente seguro'),
            ('suspeito', 'Suspeito'),
            ('perigoso', 'Potencialmente perigoso'),
        ],
        blank=True,
        null=True
    )
    
    motivo_link = models.TextField(blank=True, null=True)
    
        
    

    def __str__(self):
        return f"{self.get_tipo_autor_display()} - {self.criado_em}"
    
class AnexoMensagemChat(models.Model):
    mensagem = models.ForeignKey(
        MensagemChatDenuncia,
        on_delete=models.CASCADE,
        related_name='anexos'
    )

    arquivo = models.FileField(
        upload_to='anexos_chat/',
        blank=True,
        null=True
    )

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Anexo da mensagem #{self.mensagem.id}"


