from django import forms
from .models import Denuncia

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def clean(self, data, initial=None):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            return data

        return [data]

class DenunciaForm(forms.ModelForm):
    arquivo = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
             'multiple': True,
             'accept': (
                    'image/*',
                    'video/*,'
                    'audio/*,'
                    'application/pdf',
                )
        })
    )
    link = forms.URLField(required=False)

    class Meta:
        model = Denuncia
        fields = ['tipo', 'descricao', 'anonima', 'exibir_setor', 'arquivo', 'link']
        
class RespostaDenunciaForm(forms.ModelForm):
    class Meta:
        model = Denuncia
        fields = ['status', 'resposta_rh']
        
from .models import FeedbackIA


class FeedbackIAForm(forms.ModelForm):
    class Meta:
        model = FeedbackIA
        fields = ['tipo_correto']