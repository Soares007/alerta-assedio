from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DenunciaForm
from .models import Denuncia

@login_required
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
            
            return redirect('sucesso')
        
    else:
        form = DenunciaForm()

    return render(request, 'denuncias/form.html', {'form': form})

def sucesso(request):
    return render(request, 'denuncias/sucesso.html')

def home(request):
    return render(request, 'denuncias/home.html')