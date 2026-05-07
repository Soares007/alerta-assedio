from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DenunciaForm, RespostaDenunciaForm
from .models import Denuncia, Notificacao
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail, EmailMultiAlternatives


def enviar_email_html(assunto, mensagem_texto, mensagem_html, destinatarios):
    email = EmailMultiAlternatives(
        subject=assunto,
        body=mensagem_texto,
        from_email='sistema@denuncias.com',
        to=destinatarios
    )

    email.attach_alternative(mensagem_html, "text/html")
    email.send()
    
@login_required
def dashboard(request):
    ui_rh = request.user.groups.filter(name='RH').exists()
    ui_admin = request.user.groups.filter(name='Administrador').exists()
    ui_superuser = request.user.is_superuser

    if ui_rh or ui_admin or ui_superuser:
        denuncias = Denuncia.objects.all()
    else:
        denuncias = Denuncia.objects.filter(usuario=request.user)

    total = denuncias.count()

    moral = denuncias.filter(tipo='moral').count()
    sexual = denuncias.filter(tipo='sexual').count()
    abuso = denuncias.filter(tipo='abuso').count()

    recebidas = denuncias.filter(status='recebida').count()
    analise = denuncias.filter(status='analise').count()
    resolvidas = denuncias.filter(status='resolvida').count()

    context = {
        'total': total,
        'moral': moral,
        'sexual': sexual,
        'abuso': abuso,
        'recebidas': recebidas,
        'analise': analise,
        'resolvidas': resolvidas,
    }

    return render(request, 'denuncias/dashboard.html', context)

@login_required
def minhas_denuncias(request):
    denuncias = Denuncia.objects.filter(usuario=request.user).order_by('-data_criacao')
    return render(request, 'denuncias/minhas_denuncias.html', {'denuncias': denuncias})

@login_required
def todas_denuncias(request):
    ui_rh = request.user.groups.filter(name='RH').exists()
    ui_admin = request.user.groups.filter(name='Administrador').exists()
    ui_superuser = request.user.is_superuser
    
    if not (ui_rh or ui_admin or ui_superuser):
        return redirect('home')
    
    denuncias = Denuncia.objects.all().order_by('-data_criacao')
    
    return render(request, 'denuncias/todas_denuncias.html', {
        'denuncias': denuncias
    })
    
@login_required
def criar_denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST)

        if form.is_valid():
            denuncia = form.save(commit=False)
            denuncia.usuario = request.user
            denuncia.save()

            from django.contrib.auth.models import User
            
            usuarios_rh = User.objects.filter(groups__name='RH')
            
            emails_rh = [u.email for u in usuarios_rh if u.email]
            
            if emails_rh:
                send_mail(
                    subject='Nova denúncia recebida',
                    message='Uma nova denúncia foi registrada no sistema. Acesse o painel para verificar.',
                    from_email=emails_rh,
                    recipient_list=emails_rh,
                    fail_silently=True,
                    
                )
            
            return redirect('sucesso')
        
    else:
        form = DenunciaForm()

    return render(request, 'denuncias/form.html', {'form': form})

def sucesso(request):
    return render(request, 'denuncias/sucesso.html')

def home(request):
    return render(request, 'denuncias/home.html')

@login_required
def painel_rh(request, denuncia_id=None):
    eh_rh = request.user.groups.filter(name='RH').exists()
    eh_admin = request.user.groups.filter(name='Administrador').exists()
    eh_superuser = request.user.is_superuser

    if not (eh_rh or eh_admin or eh_superuser):
        return redirect('home')

    denuncias = Denuncia.objects.all().order_by('-data_criacao')
    denuncia_selecionada = None
    form = None

    if denuncia_id:
        denuncia_selecionada = Denuncia.objects.get(id=denuncia_id)

        if request.method == 'POST':
            form = RespostaDenunciaForm(request.POST, instance=denuncia_selecionada)

            if form.is_valid():
                denuncia_atualizada = form.save()
                
                
                Notificacao.objects.create(
                    usuario=denuncia_atualizada.usuario,
                    titulo='Nova resposta do RH',
                    mensagem='Sua denúncia recebeu uma resposta ou atualização de status'
                )
                
                if denuncia_atualizada.usuario.email:
                  enviar_email_html(
        assunto='Sua denúncia recebeu uma atualização',
        mensagem_texto='Sua denúncia recebeu uma resposta ou teve o status atualizado.',
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
        destinatarios=[denuncia_atualizada.usuario.email]
    )
                
                messages.success(request, 'Resposta enviada com sucesso!')

                return redirect(
                    'painel_rh_detalhe',
                    denuncia_id=denuncia_selecionada.id
                )
        else:
            form = RespostaDenunciaForm(instance=denuncia_selecionada)

    return render(request, 'denuncias/painel_rh.html', {
        'denuncias': denuncias,
        'denuncia_selecionada': denuncia_selecionada,
        'form': form,
    })
    
@login_required
def marcar_notificacoes_lidas(request):
    if request.method == 'POST':
        Notificacao.objects.filter(
            usuario=request.user,
            lida=False
        ).update(lida=True)

        return JsonResponse({
            'status': 'ok'
        })

    return JsonResponse({
        'status': 'erro'
    })