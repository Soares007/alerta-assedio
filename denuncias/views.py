from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DenunciaForm
from .models import Denuncia

@login_required
def dashboard(request):
    total = Denuncia.objects.count()
    
    moral = Denuncia.objects.filter(tipo='moral').count()
    sexual = Denuncia.objects.filter(tipo='sexual').count()
    abuso = Denuncia.objects.filter(tipo='abuso').count()
    
    recebidas = Denuncia.objects.filter(status='recebida').count()
    analise = Denuncia.objects.filter(status='analise').count()
    resolvidas = Denuncia.objects.filter(status='resolvida').count()
    
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
    

def minhas_denuncias(request):
    denuncias = Denuncia.objects.filter(usuario=request.user)
    return render(request, 'denuncias/minhas_denuncias.html', {'denuncias': denuncias})
    
def criar_denuncia(request):
    if request.method == 'POST':
        form = DenunciaForm(request.POST)

        if form.is_valid():
            denuncia = form.save(commit=False)
            
            if denuncia.anonima:
                denuncia.usuario = None
            else:
                denuncia.usuario = request.user
                
            denuncia.save()
            return redirect('sucesso')
        
    else:
        form = DenunciaForm()

    return render(request, 'denuncias/form.html', {'form': form})

def sucesso(request):
    return render(request, 'denuncias/sucesso.html')