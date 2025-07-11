from django import forms
from django.contrib.auth.models import User
from .models import Chamado, Interacao
from cadastros.models import Bloco, Sala, TipoServico
from inventario.models import Ativo

class ChamadoForm(forms.ModelForm):
    bloco = forms.ModelChoiceField(queryset=Bloco.objects.all(), label="Bloco do Serviço", empty_label="--- Selecione um Bloco ---")
    sala = forms.ModelChoiceField(queryset=Sala.objects.none(), label="Sala do Bloco")
    tipo_servico = forms.ModelChoiceField(queryset=TipoServico.objects.all(), label="Tipo de Serviço", empty_label="--- Selecione um Tipo de Serviço ---")
    ativo = forms.ModelChoiceField(queryset=Ativo.objects.none(), label="Ativo Específico (Opcional)", required=False)
    class Meta:
        model = Chamado
        fields = ['email_solicitante', 'bloco', 'sala', 'tipo_servico', 'ativo', 'descricao', 'foto']
        widgets = {'descricao': forms.Textarea(attrs={'rows': 4})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        if 'foto' in self.fields:
            self.fields['foto'].widget.attrs['accept'] = 'image/*'
            self.fields['foto'].widget.attrs['capture'] = 'environment'
        if 'bloco' in self.data:
            try:
                bloco_id = int(self.data.get('bloco'))
                self.fields['sala'].queryset = Sala.objects.filter(bloco_id=bloco_id).order_by('nome')
            except (ValueError, TypeError): pass
        elif self.instance.pk:
            self.fields['sala'].queryset = self.instance.bloco.sala_set.order_by('nome')
        if 'sala' in self.data:
            try:
                sala_id = int(self.data.get('sala'))
                self.fields['ativo'].queryset = Ativo.objects.filter(localizacao_id=sala_id).order_by('nome')
            except (ValueError, TypeError): pass
        elif self.instance.pk and self.instance.sala:
            self.fields['ativo'].queryset = self.instance.sala.ativo_set.order_by('nome')

class ConsultaChamadoForm(forms.Form):
    email_solicitante = forms.EmailField(label="Seu E-mail")
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email_solicitante'].widget.attrs['class'] = 'form-control form-control-lg'
        self.fields['email_solicitante'].widget.attrs['placeholder'] = 'Digite o e-mail usado na abertura dos chamados...'

class InteracaoForm(forms.ModelForm):
    class Meta:
        model = Interacao
        fields = ['mensagem']
        widgets = {'mensagem': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Digite sua mensagem ou atualização aqui...'}),}
        labels = {'mensagem': ''}

class ChamadoUpdateForm(forms.ModelForm):
    tecnico_responsavel = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Técnicos'), required=False, label="Técnico Responsável", empty_label="--- Nenhum Técnico Atribuído ---")
    class Meta:
        model = Chamado
        fields = ['status', 'tecnico_responsavel', 'observacoes_tecnicas']
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChamadoUpdateForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        if self.user and not self.user.groups.filter(name='Coordenadores').exists():
            if 'tecnico_responsavel' in self.fields:
                self.fields['tecnico_responsavel'].disabled = True

class AtribuicaoTecnicoForm(forms.Form):
    tecnico_responsavel = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Técnicos'), label="", widget=forms.Select(attrs={'class': 'form-select form-select-sm'}))

class PendenciaForm(forms.Form):
    motivo = forms.CharField(label="Motivo da Pendência", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Aguardando chegada de peça.'}))

class ChamadoFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[('', 'Todos os Status')] + Chamado.STATUS_CHOICES, required=False, label="Filtrar por Status")
    tecnico_responsavel = forms.ModelChoiceField(queryset=User.objects.filter(groups__name='Técnicos'), required=False, label="Filtrar por Técnico", empty_label="Todos os Técnicos")
    incluir_arquivados = forms.BooleanField(label="Incluir Finalizados", required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

class AvaliacaoForm(forms.ModelForm):
    NOTA_CHOICES = [('', '--- Selecione uma nota ---'), (5, '5 Estrelas - Excelente'), (4, '4 Estrelas - Bom'), (3, '3 Estrelas - Regular'), (2, '2 Estrelas - Ruim'), (1, '1 Estrela - Péssimo')]
    nota_avaliacao = forms.ChoiceField(choices=NOTA_CHOICES, label="Sua Avaliação", widget=forms.Select(attrs={'class': 'form-select'}))
    class Meta:
        model = Chamado
        fields = ['nota_avaliacao', 'comentario_avaliacao']
        labels = {'comentario_avaliacao': 'Comentário (opcional)'}
        widgets = {'comentario_avaliacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})}

class ReaberturaForm(forms.Form):
    motivo = forms.CharField(label="Motivo da Reabertura", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: O problema voltou a acontecer.'}))

class CancelamentoForm(forms.Form):
    motivo = forms.CharField(label="Motivo do Cancelamento", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ex: Chamado aberto em duplicidade.'}))

class PublicChamadoFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', 'Todos os Status')] + Chamado.STATUS_CHOICES,
        required=False,
        label="Filtrar por Status",
        widget=forms.Select(attrs={'class': 'form-select'})
    )