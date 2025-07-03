from django import forms
from .models import Sala, TipoPiso, TipoForro, TipoPintura, TipoPorta

class SalaAdminForm(forms.ModelForm):
    # Explicitamente definimos os campos de tipo, garantindo que não são obrigatórios
    tipo_piso = forms.ModelChoiceField(queryset=TipoPiso.objects.all(), required=False, label="Tipo de Piso")
    tipo_forro = forms.ModelChoiceField(queryset=TipoForro.objects.all(), required=False, label="Tipo de Forro")
    tipo_pintura = forms.ModelChoiceField(queryset=TipoPintura.objects.all(), required=False, label="Tipo de Pintura")
    tipo_porta = forms.ModelChoiceField(queryset=TipoPorta.objects.all(), required=False, label="Tipo de Porta")

    class Meta:
        model = Sala
        # Inclui todos os campos do modelo Sala no formulário
        fields = '__all__'