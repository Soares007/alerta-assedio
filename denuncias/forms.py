from django import forms
from .models import Denuncia

class DenunciaForm(forms.ModelForm):
    arquivo = forms.FileField(required=False)
    link = forms.URLField(required=False)

    class Meta:
        model = Denuncia
        fields = ['tipo', 'descricao', 'anonima', 'exibir_setor', 'arquivo', 'link']
        
class RespostaDenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['status', 'resposta_rh']