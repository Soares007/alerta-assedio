from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DenunciaForm

@login_required
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