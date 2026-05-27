from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DenunciaForm, RespostaDenunciaForm, FeedbackIA
from .models import Denuncia, Notificacao,  AnexoDenuncia, PerfilUsuario,  ChatDenuncia, MensagemChatDenuncia, AnexoMensagemChat
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import JsonResponse
import os
from django.contrib import messages
from .ia.gemini_api import (
    analisar_relato_com_fallback,
    gerar_resumo_com_fallback,
    analisar_link_com_fallback,
    responder_chat_com_fallback
)
import re


def criar_notificacao_usuario(usuario, titulo, mensagem, tipo="geral"):
    if not usuario:
        return

    Notificacao.objects.create(usuario=usuario, titulo=titulo, mensagem=mensagem)

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"user_{usuario.id}",
        {
            "type": "enviar_notificacao",
            "titulo": titulo,
            "mensagem": mensagem,
            "tipo": tipo,
        },
    )


def enviar_email_html(assunto, mensagem_texto, mensagem_html, destinatarios):
    email = EmailMultiAlternatives(
        subject=assunto,
        body=mensagem_texto,
        from_email="sistema@denuncias.com",
        to=destinatarios,
    )

    email.attach_alternative(mensagem_html, "text/html")
    email.send()


@login_required
def dashboard(request):
    eh_rh = request.user.groups.filter(name="RH").exists()
    eh_admin = request.user.groups.filter(name="Administrador").exists()
    eh_superuser = request.user.is_superuser

    if eh_rh or eh_admin or eh_superuser:
        denuncias = Denuncia.objects.all()
    else:
        denuncias = Denuncia.objects.filter(usuario=request.user)

    total = denuncias.count()

    recebidas = denuncias.filter(status="recebida").count()
    analise = denuncias.filter(status="analise").count()
    resolvidas = denuncias.filter(status="resolvida").count()

    tipos_dict = dict(Denuncia.TIPOS)

    por_tipo = (
        denuncias
        .values("tipo")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    por_setor = (
        denuncias.filter(setor__isnull=False)
        .values("setor__nome")
        .annotate(total=Count("id"))
        .order_by("-total")
    )

    por_dia = (
        denuncias.annotate(dia=TruncDate("data_criacao"))
        .values("dia")
        .annotate(total=Count("id"))
        .order_by("dia")
    )

    context = {
        "total": total,
        "recebidas": recebidas,
        "analise": analise,
        "resolvidas": resolvidas,

        "tipos_labels": [
            tipos_dict.get(item["tipo"], item["tipo"])
            for item in por_tipo
        ],
        "tipos_valores": [
            item["total"]
            for item in por_tipo
        ],

        "setores_labels": [item["setor__nome"] for item in por_setor],
        "setores_valores": [item["total"] for item in por_setor],
        "dias_labels": [item["dia"].strftime("%d/%m") for item in por_dia],
        "dias_valores": [item["total"] for item in por_dia],
    }

    return render(request, "denuncias/dashboard.html", context)

@login_required
def minhas_denuncias(request):
    busca = request.GET.get("busca", "")
    status = request.GET.get("status", "")
    tipo = request.GET.get("tipo", "")
    page = request.GET.get("page", 1)

    denuncias = Denuncia.objects.filter(usuario=request.user).order_by("-data_criacao")

    if busca:
        denuncias = denuncias.filter(descricao__icontains=busca)

    if status:
        denuncias = denuncias.filter(status=status)

    if tipo:
        denuncias = denuncias.filter(tipo=tipo)

    paginator = Paginator(denuncias, 5)
    denuncias_paginadas = paginator.get_page(page)

    context = {
        "denuncias": denuncias_paginadas,
        "busca": busca,
        "status_filtro": status,
        "tipo_filtro": tipo,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "denuncias/partials/lista_minhas_denuncias.html",
            context,
            request=request
        )

        return JsonResponse({
            "html": html
        })

    return render(request, "denuncias/minhas_denuncias.html", context)


@login_required
def denuncias_arquivadas(request):
    ui_rh = request.user.groups.filter(name="RH").exists()
    ui_admin = request.user.groups.filter(name="Administrador").exists()
    ui_superuser = request.user.is_superuser

    if not (ui_rh or ui_admin or ui_superuser):
        return redirect("home")

    busca = request.GET.get("busca", "")
    tipo = request.GET.get("tipo", "")
    gravidade = request.GET.get("gravidade", "")
    pagina = request.GET.get("page", 1)

    denuncias = Denuncia.objects.filter(arquivada=True).order_by("-data_arquivamento")

    if busca:
        denuncias = denuncias.filter(descricao__icontains=busca)

    if tipo:
        denuncias = denuncias.filter(tipo=tipo)

    if gravidade:
        denuncias = denuncias.filter(gravidade=gravidade)

    paginator = Paginator(denuncias, 5)
    denuncias_paginadas = paginator.get_page(pagina)

    context = {
        "denuncias": denuncias_paginadas,
        "busca": busca,
        "tipo_filtro": tipo,
        "gravidade_filtro": gravidade,
    }

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        html = render_to_string(
            "denuncias/partials/lista_arquivadas.html",
            context,
            request=request
        )

        return JsonResponse({
            "html": html
        })

    return render(request, "denuncias/denuncias_arquivadas.html", context)
    
@login_required
def criar_denuncia(request):
    if request.method == "POST":
        form = DenunciaForm(request.POST, request.FILES)

        if form.is_valid():
            denuncia = form.save(commit=False)
            denuncia.usuario = request.user

            resultado_ia = analisar_relato_com_fallback(denuncia.descricao)
            

            denuncia.resumo_ia = gerar_resumo_com_fallback(
                denuncia.descricao
            )
            
            print("IA UTILIZADA RELATO:", resultado_ia.get("origem_ia"))
            print("RESUMO GERADO:", denuncia.resumo_ia)          

            denuncia.tipo = resultado_ia.get("tipo") or denuncia.tipo
            denuncia.gravidade = resultado_ia.get("gravidade", "baixa")

            prioridades = {
                "baixa": 1,
                "media": 2,
                "alta": 3,
                "critica": 4,
            }

            denuncia.prioridade_ia = prioridades.get(
                denuncia.gravidade,
                1
            )

            denuncia.urgente = resultado_ia.get("urgente", False)

            perfil = PerfilUsuario.objects.filter(
                usuario=request.user
            ).first()

            if perfil:
                denuncia.setor = perfil.setor

            denuncia.save()

            arquivos = request.FILES.getlist("arquivo")
            link = form.cleaned_data.get("link", "").strip()

            for arquivo in arquivos:
                valido, erro = validar_anexo(arquivo)

                if not valido:
                    denuncia.delete()
                    messages.error(request, erro)
                    return render(
                        request,
                        "denuncias/form.html",
                        {"form": form}
                    )

                AnexoDenuncia.objects.create(
                    denuncia=denuncia,
                    arquivo=arquivo
                )

            if link:
                if not link.startswith(("http://", "https://")):
                    link = "https://" + link

                resultado_link = analisar_link_com_fallback(link)

                AnexoDenuncia.objects.create(
                    denuncia=denuncia,
                    link=link,
                    status_link=resultado_link.get("status"),
                    motivo_link=resultado_link.get("motivo")
                )

            usuarios_rh = User.objects.filter(groups__name="RH")
            emails_rh = [u.email for u in usuarios_rh if u.email]

            for usuario_rh in usuarios_rh:
                criar_notificacao_usuario(
                    usuario=usuario_rh,
                    titulo="Nova denúncia recebida",
                    mensagem="Uma nova denúncia foi registrada no sistema.",
                    tipo="nova_denuncia",
                )

            if emails_rh:
                enviar_email_html(
                    assunto="Nova denúncia recebida",
                    mensagem_texto="Uma nova denúncia foi registrada no sistema.",
                    mensagem_html=f"""
                        <div style="font-family: Arial, sans-serif; background:#f4f6f8; padding:30px;">
                            <div style="max-width:600px; margin:auto; background:white; padding:25px; border-radius:12px;">
                                <h2 style="color:#1f2937;">Nova denúncia recebida</h2>

                                <p>Uma nova denúncia foi registrada no sistema.</p>

                                <p>
                                    <strong>Tipo:</strong> {denuncia.get_tipo_display()}<br>
                                    <strong>Anônima:</strong> {"Sim" if denuncia.anonima else "Não"}
                                </p>

                                <p style="margin-top:20px;">
                                    Acesse o painel do RH para analisar e responder.
                                </p>
                            </div>
                        </div>
                    """,
                    destinatarios=emails_rh,
                )

            return redirect("sucesso")

    else:
        form = DenunciaForm()

    return render(request, "denuncias/form.html", {"form": form})


def sucesso(request):
    return render(request, "denuncias/sucesso.html")


def home(request):
    return render(request, "denuncias/home.html")


@login_required
def painel_rh(request, denuncia_id=None):
    from django.utils import timezone
    from datetime import timedelta
    
    limite_arquivamento = timezone.now() - timedelta(days=30)
    
    Denuncia.objects.filter(
        status='resolvida',
        arquivada=False,
        data_criacao__lte=limite_arquivamento
    ).update(
        arquivada=True,
        data_arquivamento=timezone.now()
    )
    
    eh_rh = request.user.groups.filter(name="RH").exists()
    eh_admin = request.user.groups.filter(name="Administrador").exists()
    eh_superuser = request.user.is_superuser

    if not (eh_rh or eh_admin or eh_superuser):
        return redirect("home")

    tipo = request.GET.get("tipo")
    anonima = request.GET.get("anonima")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")
    ordem = request.GET.get("ordem", "recentes")
    limite = request.GET.get("limite", 5)

    try:
        limite = int(limite)
    except ValueError:
        limite = 5

    denuncias_base = Denuncia.objects.filter(arquivada=False)

    if tipo:
        denuncias_base = denuncias_base.filter(tipo=tipo)

    if anonima == "sim":
        denuncias_base = denuncias_base.filter(anonima=True)

    if anonima == "nao":
        denuncias_base = denuncias_base.filter(anonima=False)

    if data_inicio:
        denuncias_base = denuncias_base.filter(data_criacao__date__gte=data_inicio)

    if data_fim:
        denuncias_base = denuncias_base.filter(data_criacao__date__lte=data_fim)

    if ordem == 'antigas':
        denuncias_base = denuncias_base.order_by(
            '-prioridade_ia',
            'data_criacao'
        )
    else:
        denuncias_base = denuncias_base.order_by(
            '-prioridade_ia',
            '-data_criacao'
        )
            
    recebidas_lista = denuncias_base.filter(status="recebida")
    analise_lista = denuncias_base.filter(status="analise")
    resolvidas_lista = denuncias_base.filter(status="resolvida")

    denuncias_recebidas = Paginator(recebidas_lista, limite).get_page(
        request.GET.get("page_recebidas")
    )

    denuncias_analise = Paginator(analise_lista, limite).get_page(
        request.GET.get("page_analise")
    )

    denuncias_resolvidas = Paginator(resolvidas_lista, limite).get_page(
        request.GET.get("page_resolvidas")
    )

    denuncia_selecionada = None
    form = None

    if denuncia_id:
        denuncia_selecionada = Denuncia.objects.get(id=denuncia_id)

        if request.method == "POST":
            form = RespostaDenunciaForm(request.POST, instance=denuncia_selecionada)

            if form.is_valid():
                denuncia_atualizada = form.save()

                if denuncia_atualizada.usuario:
                    Notificacao.objects.create(
                        usuario=denuncia_atualizada.usuario,
                        titulo="Nova resposta do RH",
                        mensagem="Sua denúncia recebeu uma resposta ou atualização de status.",
                    )

                    channel_layer = get_channel_layer()

                    async_to_sync(channel_layer.group_send)(
                        f"user_{denuncia_atualizada.usuario.id}",
                        {
                            "type": "enviar_notificacao",
                            "titulo": "Nova resposta do RH",
                            "mensagem": "Sua denúncia recebeu uma resposta ou atualização de status.",
                        },
                    )

                    if denuncia_atualizada.usuario.email:
                        enviar_email_html(
                            assunto="Sua denúncia recebeu uma atualização",
                            mensagem_texto="Sua denúncia recebeu uma resposta ou teve o status atualizado.",
                            mensagem_html=f"""
                                <div style="font-family: Arial, sans-serif; background:#f4f6f8; padding:30px;">
                                    <div style="max-width:600px; margin:auto; background:white; padding:25px; border-radius:12px;">
                                        <h2 style="color:#1f2937;">Atualização da sua denúncia</h2>

                                        <p>Sua denúncia recebeu uma nova atualização.</p>

                                        <p>
                                            <strong>Status:</strong> {denuncia_atualizada.get_status_display()}
                                        </p>

                                        <p>
                                            <strong>Resposta do RH:</strong><br>
                                            {denuncia_atualizada.resposta_rh or "Ainda sem resposta escrita."}
                                        </p>

                                        <p style="margin-top:20px;">
                                            Acesse o sistema para acompanhar os detalhes.
                                        </p>
                                    </div>
                                </div>
                            """,
                            destinatarios=[denuncia_atualizada.usuario.email],
                        )

                messages.success(request, "Resposta enviada com sucesso!")

                return redirect("painel_rh")
        else:
            form = RespostaDenunciaForm(instance=denuncia_selecionada)
            
    
    tipos_filtro = [
        {
            "valor": valor,
            "nome": nome
        }
        for valor, nome in Denuncia.TIPOS
    ]

    return render(
        request,
        "denuncias/painel_rh.html",
        {
            "denuncias_recebidas": denuncias_recebidas,
            "denuncias_analise": denuncias_analise,
            "denuncias_resolvidas": denuncias_resolvidas,
            "denuncia_selecionada": denuncia_selecionada,
            "form": form,
            "tipos_filtro": tipos_filtro,
            "anonima_filtro": anonima,
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "ordem": ordem,
            "limite": limite,
        },
    )


@login_required
def marcar_notificacoes_lidas(request):
    if request.method == "POST":
        Notificacao.objects.filter(usuario=request.user, lida=False).update(lida=True)

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "erro"})


@login_required
def api_notificacoes(request):
    notificacoes = Notificacao.objects.filter(usuario=request.user).order_by(
        "-data_criacao"
    )[:5]

    data = []

    for n in notificacoes:
        data.append(
            {
                "titulo": n.titulo,
                "mensagem": n.mensagem,
                "data": n.data_criacao.strftime("%d/%m/%Y %H:%M"),
            }
        )

    total_nao_lidas = Notificacao.objects.filter(
        usuario=request.user, lida=False
    ).count()

    return JsonResponse({"notificacoes": data, "total_nao_lidas": total_nao_lidas})


@login_required
def alterar_status_denuncia(request, denuncia_id):
    eh_rh = request.user.groups.filter(name="RH").exists()
    eh_admin = request.user.groups.filter(name="Administrador").exists()
    eh_superuser = request.user.is_superuser

    if not (eh_rh or eh_admin or eh_superuser):
        return JsonResponse({"status": "erro"}, status=403)

    if request.method == "POST":
        denuncia = Denuncia.objects.get(id=denuncia_id)
        novo_status = request.POST.get("status")

        if novo_status in ["recebida", "analise", "resolvida"]:
            status_antigo = denuncia.status

            denuncia.status = novo_status
            denuncia.save()

            if status_antigo != novo_status:
                criar_notificacao_usuario(
                    usuario=denuncia.usuario,
                    titulo="Status da denúncia atualizado",
                    mensagem=f"Sua denúncia agora está como: {denuncia.get_status_display()}.",
                    tipo="status_denuncia",
                )

                channel_layer = get_channel_layer()

                async_to_sync(channel_layer.group_send)(
                    f"user_{denuncia.usuario.id}",
                    {
                        "type": "enviar_notificacao",
                        "titulo": "Status da denúncia atualizado",
                        "mensagem": f"Sua denúncia agora está como: {denuncia.get_status_display()}.",
                    },
                )

                if denuncia.usuario.email:
                    enviar_email_html(
                        assunto="Status da sua denúncia foi atualizado",
                        mensagem_texto=f"Sua denúncia agora está como: {denuncia.get_status_display()}.",
                        mensagem_html=f"""
                            <div style="font-family: Arial, sans-serif; background:#f4f6f8; padding:30px;">
                                <div style="max-width:600px; margin:auto; background:white; padding:25px; border-radius:12px;">
                                    <h2 style="color:#1f2937;">Status atualizado</h2>

                                    <p>Sua denúncia teve uma alteração de status.</p>

                                    <p>
                                        <strong>Novo status:</strong> {denuncia.get_status_display()}
                                    </p>

                                    <p style="margin-top:20px;">
                                        Acesse o sistema para acompanhar os detalhes.
                                    </p>
                                </div>
                            </div>
                        """,
                        destinatarios=[denuncia.usuario.email],
                    )

            return JsonResponse({"status": "ok", "novo_status": novo_status})

    return JsonResponse({"status": "erro"}, status=400)


@login_required
def limpar_notificacoes(request):
    if request.method == "POST":
        Notificacao.objects.filter(usuario=request.user).delete()

        return JsonResponse({"status": "ok"})

    return JsonResponse({"status": "erro"}, status=400)



def analisar_relato(request):
    if request.method != 'POST':
        return JsonResponse({
            'tipo': '',
            'titulo': 'Método inválido',
            'mensagem': 'Envie um relato para análise.',
            'confianca': 0
        }, status=400)

    texto = request.POST.get('texto', '')

    resultado = analisar_relato_com_fallback(texto)

    if not isinstance(resultado, dict):
        resultado = {
            'tipo': '',
            'titulo': 'Não identificado com clareza',
            'mensagem': str(resultado),
            'confianca': 0
        }

    return JsonResponse(resultado)


@login_required
def feedback_ia(request):
    eh_rh = request.user.groups.filter(name='RH').exists()
    eh_admin = request.user.groups.filter(name='Administrador').exists()
    eh_superuser = request.user.is_superuser

    if not (eh_rh or eh_admin or eh_superuser):
        return redirect('home')

    busca = request.GET.get('busca', '')
    tipo = request.GET.get('tipo', '')
    pagina = request.GET.get('page')

    denuncias = Denuncia.objects.all().order_by('-data_criacao')

    if busca:
        denuncias = denuncias.filter(descricao__icontains=busca)

    if tipo:
        denuncias = denuncias.filter(tipo=tipo)

    if request.method == 'POST':
        denuncia_id = request.POST.get('denuncia_id')
        tipo_correto = request.POST.get('tipo_correto')

        denuncia = Denuncia.objects.get(id=denuncia_id)

        FeedbackIA.objects.create(
            texto=denuncia.descricao,
            tipo_sugerido=denuncia.tipo,
            tipo_correto=tipo_correto,
            usuario=request.user
        )

        denuncia.tipo = tipo_correto
        denuncia.save()

        messages.success(request, 'Correção salva com sucesso!')

        return redirect('feedback_ia')

    paginator = Paginator(denuncias, 8)
    denuncias_paginadas = paginator.get_page(pagina)

    return render(request, 'denuncias/feedback_ia.html', {
        'denuncias': denuncias_paginadas,
        'busca': busca,
        'tipo_filtro': tipo,
    })
    
@login_required
def arquivar_denuncia(request, denuncia_id):
    ui_rh = request.user.groups.filter(name="RH").exists()
    ui_admin = request.user.groups.filter(name="Administrador").exists()
    ui_superuser = request.user.is_superuser

    if not (ui_rh or ui_admin or ui_superuser):
        return redirect("home")

    if request.method == "POST":
        denuncia = Denuncia.objects.get(id=denuncia_id)
        denuncia.arquivada = True
        denuncia.data_arquivamento = timezone.now()
        denuncia.save()

        messages.success(request, "Denúncia arquivada com sucesso.")

    return redirect("painel_rh")

def validar_anexo(arquivo):
    extensoes_permitidas = [
        '.jpg', '.jpeg', '.png', '.webp', '.gif',
        '.mp4', '.webm', '.ogg',
        '.mp3', '.wav',
        '.pdf'
    ]

    tipos_permitidos = [
        'image/jpeg',
        'image/png',
        'image/webp',
        'image/gif',
        'video/mp4',
        'video/webm',
        'video/ogg',
        'audio/mpeg',
        'audio/wav',
        'audio/ogg',
        'application/pdf'
    ]

    tamanho_maximo = 20 * 1024 * 1024

    nome = arquivo.name.lower()
    extensao = os.path.splitext(nome)[1]
    tipo = arquivo.content_type
    tamanho = arquivo.size

    if extensao not in extensoes_permitidas:
        return False, f'O arquivo "{arquivo.name}" possui uma extensão não permitida.'

    if tipo not in tipos_permitidos:
        return False, f'O arquivo "{arquivo.name}" possui um tipo inválido.'

    if tamanho > tamanho_maximo:
        return False, f'O arquivo "{arquivo.name}" ultrapassa o limite de 20MB.'

    return True, ''

def extrair_primeiro_link(texto):
    padrao = r'(https?://[^\s]+|www\.[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}[^\s]*)'
    resultado = re.search(padrao, texto)

    if not resultado:
        return None

    link = resultado.group(0).strip()

    if not link.startswith(("http://", "https://")):
        link = "https://" + link

    return link

@login_required
def chat_denuncia(request, denuncia_id):
    denuncia = Denuncia.objects.get(id=denuncia_id)

    eh_rh = request.user.groups.filter(name="RH").exists()
    eh_admin = request.user.groups.filter(name="Administrador").exists()
    eh_superuser = request.user.is_superuser
    eh_dono = denuncia.usuario == request.user

    if not (eh_dono or eh_rh or eh_admin or eh_superuser):
        return redirect("home")

    chat, criado = ChatDenuncia.objects.get_or_create(
        denuncia=denuncia
    )

    def retornar_chat_json():
        mensagens = chat.mensagens.all().order_by("criado_em")

        html = render_to_string(
            "denuncias/partials/chat_mensagens.html",
            {"mensagens": mensagens},
            request=request
        )

        return JsonResponse({
            "html": html
        })

    if request.method == "POST":
        acao = request.POST.get("acao")

        if acao == "ia":
            tipo_pedido = request.POST.get("tipo_pedido", "geral")
             
            try:
                mensagens_chat = chat.mensagens.all().order_by("criado_em")[:20]

                contexto = f"""
DENÚNCIA:
ID: {denuncia.id}
Tipo: {denuncia.get_tipo_display()}
Status: {denuncia.get_status_display()}
Gravidade: {denuncia.get_gravidade_display()}
Resumo IA: {denuncia.resumo_ia or "Sem resumo"}
Descrição: {denuncia.descricao}

PEDIDO DO USUÁRIO:
{tipo_pedido}
"""

                for m in mensagens_chat:
                    contexto += f"""
[{m.tipo_autor.upper()}]
{m.mensagem}
"""

                resposta_ia = responder_chat_com_fallback(contexto)

                MensagemChatDenuncia.objects.create(
                    chat=chat,
                    usuario=None,
                    tipo_autor="ia",
                    mensagem=resposta_ia,
                    anonimo=True
                )

            except Exception as erro:
                print("ERRO AO GERAR RESPOSTA IA NO CHAT:", erro)

                MensagemChatDenuncia.objects.create(
                    chat=chat,
                    usuario=None,
                    tipo_autor="ia",
                    mensagem="Não consegui responder agora. Tente novamente em alguns instantes.",
                    anonimo=True
                )

            return retornar_chat_json()

        if acao == "mensagem":
            mensagem_texto = request.POST.get("mensagem", "").strip()
            arquivos = request.FILES.getlist("arquivo")

            if mensagem_texto or arquivos:
                if eh_rh or eh_admin or eh_superuser:
                    tipo_autor = "rh"
                    anonimo = True
                else:
                    tipo_autor = "funcionario"
                    anonimo = denuncia.anonima

                link_detectado = extrair_primeiro_link(mensagem_texto)

                status_link = None
                motivo_link = None

                if link_detectado:
                    resultado_link = analisar_link_com_fallback(link_detectado)
                    status_link = resultado_link.get("status")
                    motivo_link = resultado_link.get("motivo")

                mensagem = MensagemChatDenuncia.objects.create(
                    chat=chat,
                    usuario=request.user,
                    tipo_autor=tipo_autor,
                    mensagem=mensagem_texto,
                    anonimo=anonimo,
                    link_detectado=link_detectado,
                    status_link=status_link,
                    motivo_link=motivo_link
                )

                for arquivo in arquivos:
                    valido, erro = validar_anexo(arquivo)

                    if valido:
                        AnexoMensagemChat.objects.create(
                            mensagem=mensagem,
                            arquivo=arquivo
                        )
                    else:
                        messages.error(request, erro)

                if tipo_autor == "rh" and denuncia.usuario:
                    criar_notificacao_usuario(
                        usuario=denuncia.usuario,
                        titulo=f"Nova mensagem na denúncia #{denuncia.id}",
                        mensagem=f"O RH enviou uma mensagem sobre: {denuncia.resumo_ia or denuncia.get_tipo_display()}",
                        tipo="chat_denuncia",
                    )

                elif tipo_autor == "funcionario":
                    usuarios_rh = User.objects.filter(groups__name="RH")

                    for usuario_rh in usuarios_rh:
                        criar_notificacao_usuario(
                            usuario=usuario_rh,
                            titulo=f"Nova mensagem na denúncia #{denuncia.id}",
                            mensagem=f"Nova mensagem no chat da denúncia #{denuncia.id}.",
                            tipo="chat_denuncia",
                        )

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return retornar_chat_json()

            return redirect("chat_denuncia", denuncia_id=denuncia.id)

        if acao == "resposta_rh" and (eh_rh or eh_admin or eh_superuser):
            resposta_rh = request.POST.get("resposta_rh", "").strip()
            status = request.POST.get("status", denuncia.status)
            arquivar = request.POST.get("arquivar") == "sim"

            denuncia.resposta_rh = resposta_rh
            denuncia.status = status

            if arquivar:
                denuncia.arquivada = True
                denuncia.data_arquivamento = timezone.now()

            denuncia.save()

            MensagemChatDenuncia.objects.create(
                chat=chat,
                usuario=request.user,
                tipo_autor="sistema",
                mensagem=f"O RH atualizou a denúncia para: {denuncia.get_status_display()}."
            )

            if resposta_rh:
                MensagemChatDenuncia.objects.create(
                    chat=chat,
                    usuario=request.user,
                    tipo_autor="rh",
                    mensagem=resposta_rh,
                    anonimo=True
                )

            if denuncia.usuario:
                criar_notificacao_usuario(
                    usuario=denuncia.usuario,
                    titulo=f"Denúncia #{denuncia.id} atualizada pelo RH",
                    mensagem=f"Sua denúncia recebeu uma resposta: {denuncia.resumo_ia or denuncia.get_tipo_display()}",
                    tipo="chat_denuncia",
                )

            messages.success(request, "Resposta do RH registrada com sucesso.")

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return retornar_chat_json()

            return redirect("chat_denuncia", denuncia_id=denuncia.id)

    mensagens = chat.mensagens.all().order_by("criado_em")

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return retornar_chat_json()

    return render(request, "denuncias/chat_denuncia.html", {
        "denuncia": denuncia,
        "chat": chat,
        "mensagens": mensagens,
        "eh_rh": eh_rh or eh_admin or eh_superuser,
    })