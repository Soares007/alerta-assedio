from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DenunciaForm, RespostaDenunciaForm, FeedbackIA
from .models import Denuncia, Notificacao,  AnexoDenuncia, PerfilUsuario
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

    moral = denuncias.filter(tipo="moral").count()
    sexual = denuncias.filter(tipo="sexual").count()
    abuso = denuncias.filter(tipo="abuso").count()

    recebidas = denuncias.filter(status="recebida").count()
    analise = denuncias.filter(status="analise").count()
    resolvidas = denuncias.filter(status="resolvida").count()

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
        "moral": moral,
        "sexual": sexual,
        "abuso": abuso,
        "recebidas": recebidas,
        "analise": analise,
        "resolvidas": resolvidas,
        "setores_labels": [item["setor__nome"] for item in por_setor],
        "setores_valores": [item["total"] for item in por_setor],
        "dias_labels": [item["dia"].strftime("%d/%m") for item in por_dia],
        "dias_valores": [item["total"] for item in por_dia],
    }

    return render(request, "denuncias/dashboard.html", context)


@login_required
def minhas_denuncias(request):
    denuncias = Denuncia.objects.filter(usuario=request.user).order_by("-data_criacao")
    return render(request, "denuncias/minhas_denuncias.html", {"denuncias": denuncias})


@login_required
def todas_denuncias(request):
    ui_rh = request.user.groups.filter(name="RH").exists()
    ui_admin = request.user.groups.filter(name="Administrador").exists()
    ui_superuser = request.user.is_superuser

    if not (ui_rh or ui_admin or ui_superuser):
        return redirect("home")

    denuncias = Denuncia.objects.all().order_by("-data_criacao")

    return render(request, "denuncias/todas_denuncias.html", {"denuncias": denuncias})


@login_required
def criar_denuncia(request):
    if request.method == "POST":
        form = DenunciaForm(request.POST, request.FILES)

        if form.is_valid():
            denuncia = form.save(commit=False)
            denuncia.usuario = request.user
            
            perfil = PerfilUsuario.objects.filter(usuario=request.user).first()
            
            if perfil:
             denuncia.setor = perfil.setor
             
            denuncia.save()
            
            arquivo = form.cleaned_data.get('arquivo')
            link = form.cleaned_data.get('link')

            if arquivo or link:
                AnexoDenuncia.objects.create(
                     denuncia=denuncia,
                     arquivo=arquivo,
                     link=link
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

    denuncias_base = Denuncia.objects.all()

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

    if ordem == "antigas":
        denuncias_base = denuncias_base.order_by("data_criacao")
    else:
        denuncias_base = denuncias_base.order_by("-data_criacao")

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

    return render(
        request,
        "denuncias/painel_rh.html",
        {
            "denuncias_recebidas": denuncias_recebidas,
            "denuncias_analise": denuncias_analise,
            "denuncias_resolvidas": denuncias_resolvidas,
            "denuncia_selecionada": denuncia_selecionada,
            "form": form,
            "tipo_filtro": tipo,
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

from .ia.analisador import analisar_texto


@login_required
def analisar_relato(request):
    if request.method != 'POST':
        return JsonResponse({
            'tipo': '',
            'titulo': 'Método inválido',
            'mensagem': 'Envie um relato para análise.',
            'confianca': 0
        }, status=400)

    texto = request.POST.get('texto', '')

    resultado = analisar_texto(texto)

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