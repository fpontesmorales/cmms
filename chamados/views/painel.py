from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from urllib.parse import quote
from django.urls import reverse
from ..forms import ChamadoUpdateForm, InteracaoForm, ChamadoFilterForm, AtribuicaoTecnicoForm, PendenciaForm
from ..models import Chamado, Interacao
from .. import emails

@login_required
def painel_view(request):
    usuario_logado = request.user
    if usuario_logado.groups.filter(name='Coordenadores').exists():
        return redirect('painel_coordenador')
    elif usuario_logado.groups.filter(name='Técnicos').exists():
        return redirect('painel_tecnico')
    else:
        return redirect('admin:index')

@login_required
def painel_coordenador_view(request):
    if not request.user.groups.filter(name='Coordenadores').exists():
        raise PermissionDenied
    titulo_pagina = "Painel do Coordenador"
    chamados_qs = Chamado.objects.all()
    filter_form = ChamadoFilterForm(request.GET)
    atribuicao_form = AtribuicaoTecnicoForm()
    pendencia_form = PendenciaForm()
    cancelamento_form = PendenciaForm(prefix='cancel')

    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        tecnico = filter_form.cleaned_data.get('tecnico_responsavel')
        incluir_finalizados = filter_form.cleaned_data.get('incluir_arquivados')

        if not incluir_finalizados:
            chamados_qs = chamados_qs.exclude(status__in=['ARQUIVADO', 'CANCELADO'])
        
        if status:
            chamados_qs = chamados_qs.filter(status=status)
        if tecnico:
            chamados_qs = chamados_qs.filter(tecnico_responsavel=tecnico)
    else:
        chamados_qs = chamados_qs.exclude(status__in=['ARQUIVADO', 'CANCELADO'])

    chamados_qs = chamados_qs.order_by('-data_modificacao')

    contexto = {
        'chamados': chamados_qs,
        'titulo_pagina': titulo_pagina,
        'filter_form': filter_form,
        'atribuicao_form': atribuicao_form,
        'pendencia_form': pendencia_form,
        'cancelamento_form': cancelamento_form,
    }
    return render(request, 'chamados/painel_coordenador.html', contexto)

@login_required
def painel_tecnico_view(request):
    if not request.user.groups.filter(name='Técnicos').exists():
        raise PermissionDenied
    titulo_pagina = "Meus Chamados Atribuídos"
    chamados = Chamado.objects.filter(tecnico_responsavel=request.user).exclude(status__in=['ARQUIVADO', 'CANCELADO']).order_by('-data_modificacao')
    pendencia_form = PendenciaForm()
    contexto = {
        'chamados': chamados,
        'titulo_pagina': titulo_pagina,
        'pendencia_form': pendencia_form,
    }
    return render(request, 'chamados/painel_tecnico.html', contexto)

@login_required
def editar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    usuario_logado = request.user
    
    is_coordenador = usuario_logado.groups.filter(name='Coordenadores').exists()
    is_tecnico_responsavel = (chamado.tecnico_responsavel == usuario_logado)
    if not (is_coordenador or is_tecnico_responsavel):
        raise PermissionDenied
    
    if request.method == 'POST':
        # Instancia os dois formulários com os dados do POST ou vazios
        form_edicao = ChamadoUpdateForm(request.POST or None, instance=chamado, user=usuario_logado)
        form_interacao = InteracaoForm(request.POST or None)

        if 'salvar_edicao' in request.POST:
            if form_edicao.is_valid():
                tecnico_anterior = chamado.tecnico_responsavel
                status_anterior = chamado.status
                chamado_atualizado = form_edicao.save(commit=False)
                
                if is_coordenador and tecnico_anterior is None and chamado_atualizado.tecnico_responsavel is not None and status_anterior == 'ABERTA':
                    chamado_atualizado.status = 'DESIGNADO'
                
                chamado_atualizado.save()
                
                if chamado_atualizado.status != status_anterior:
                    emails.enviar_email_status_alterado(chamado_atualizado, request)
                if tecnico_anterior != chamado_atualizado.tecnico_responsavel and chamado_atualizado.tecnico_responsavel is not None:
                    emails.enviar_email_atribuicao_tecnico(chamado_atualizado, request)
                
                return redirect('painel')
        
        elif 'enviar_interacao' in request.POST:
            if form_interacao.is_valid():
                nova_interacao = form_interacao.save(commit=False)
                nova_interacao.chamado = chamado
                nova_interacao.usuario = usuario_logado
                nova_interacao.save()
                chamado.save()
                emails.enviar_email_nova_interacao(nova_interacao, request)
                return redirect('editar_chamado', chamado_id=chamado.id)
    else:
        # Se não for POST, instancia os formulários com os dados existentes
        form_edicao = ChamadoUpdateForm(instance=chamado, user=usuario_logado)
        form_interacao = Inter