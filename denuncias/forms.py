from django import forms
from .models import Denuncia

class DenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['tipo', 'descricao', 'anonima']
        
class RespostaDenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['status', 'resposta_rh']