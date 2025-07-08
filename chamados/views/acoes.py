from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from ..forms import AtribuicaoTecnicoForm, PendenciaForm, AvaliacaoForm, ReaberturaForm, CancelamentoForm
from ..models import Chamado, Interacao
from .. import emails

@login_required
def atribuir_tecnico_view(request, chamado_id):
    if not request.user.groups.filter(name='Coordenadores').exists():
        raise PermissionDenied
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    if request.method == 'POST':
        form = AtribuicaoTecnicoForm(request.POST)
        if form.is_valid():
            tecnico_selecionado = form.cleaned_data['tecnico_responsavel']
            chamado.tecnico_responsavel = tecnico_selecionado
            if chamado.status == 'ABERTA':
                chamado.status = 'DESIGNADO'
            chamado.save()
            emails.enviar_email_atribuicao_tecnico(chamado, request)
            emails.enviar_email_status_alterado(chamado, request)
    return redirect('painel_coordenador')

@login_required
def iniciar_analise_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    chamado.status = 'EM_ANALISE'
    chamado.save()
    emails.enviar_email_status_alterado(chamado, request)
    return redirect('painel')

@login_required
def iniciar_execucao_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    chamado.status = 'EM_EXECUCAO'
    chamado.save()
    emails.enviar_email_status_alterado(chamado, request)
    return redirect('painel')

@login_required
def finalizar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    chamado.status = 'CONCLUIDO'
    chamado.save()
    emails.enviar_email_status_alterado(chamado, request)
    return redirect('painel')

@login_required
def pendente_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    if request.method == 'POST':
        form = PendenciaForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            Interacao.objects.create(chamado=chamado, usuario=request.user, mensagem=f"Chamado colocado como pendente. Motivo: {motivo}")
            chamado.status = 'PENDENTE'
            chamado.save()
            emails.enviar_email_status_alterado(chamado, request)
    return redirect('painel')

@login_required
def cancelar_chamado_view(request, chamado_id):
    if not request.user.groups.filter(name='Coordenadores').exists():
        raise PermissionDenied
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    form = CancelamentoForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            Interacao.objects.create(chamado=chamado, usuario=request.user, mensagem=f"Chamado cancelado. Motivo: {motivo}")
            chamado.status = 'CANCELADO'
            chamado.save()
            emails.enviar_email_status_alterado(chamado, request)
            return redirect('painel')
    # Esta parte é para o caso de querermos um formulário GET no futuro, não afeta o modal atual
    return redirect('editar_chamado', chamado_id=chamado_id)

def avaliar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=chamado)
        if form.is_valid():
            form.save()
            chamado.status = 'ARQUIVADO'
            chamado.save()
            emails.enviar_email_status_alterado(chamado, request)
    return redirect('chamado_detalhe', chamado_id=chamado.id)

def reabrir_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    if request.method == 'POST':
        form = ReaberturaForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            Interacao.objects.create(chamado=chamado, usuario=None, mensagem=f"Chamado reaberto pelo solicitante. Motivo: {motivo}")
            chamado.status = 'PENDENTE'
            chamado.save()
            emails.enviar_email_status_alterado(chamado, request)
    return redirect('chamado_detalhe', chamado_id=chamado.id)