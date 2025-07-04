import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.template.loader import render_to_string
from django.urls import reverse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .forms import (
    ChamadoForm, ConsultaChamadoForm, InteracaoForm, ChamadoUpdateForm, 
    ChamadoFilterForm, AtribuicaoTecnicoForm, PendenciaForm, AvaliacaoForm,
    ReaberturaForm
)
from .models import Chamado, Interacao
from cadastros.models import Sala
from inventario.models import Ativo

def homepage_view(request):
    return render(request, 'chamados/homepage.html')

def abrir_chamado_view(request):
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            novo_chamado = form.save()
            request.session['email_solicitante'] = novo_chamado.email_solicitante
            try:
                api_key = os.environ.get('SENDGRID_API_KEY')
                if api_key:
                    assunto = f"Confirmação de Abertura de Chamado #{novo_chamado.id}"
                    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[novo_chamado.id]))
                    contexto_email = {'chamado': novo_chamado, 'url_detalhe': url_detalhe}
                    corpo_html = render_to_string('emails/confirmacao_chamado.html', contexto_email)
                    message = Mail(from_email=('infra.caucaia@ifce.edu.br', 'CMMS Infra IFCE Caucaia'), to_emails=novo_chamado.email_solicitante, subject=assunto, html_content=corpo_html)
                    sendgrid_client = SendGridAPIClient(api_key)
                    response = sendgrid_client.send(message)
            except Exception as e:
                print(f"Erro ao tentar enviar e-mail via SendGrid: {e}")
            return redirect('chamado_sucesso', chamado_id=novo_chamado.id)
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data['email_solicitante'] = request.user.email
        elif 'email_solicitante' in request.session:
            initial_data['email_solicitante'] = request.session.get('email_solicitante')
        form = ChamadoForm(initial=initial_data)
    contexto = {'form': form}
    return render(request, 'chamados/abrir_chamado.html', contexto)

def chamado_sucesso_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    contexto = {'chamado': chamado}
    return render(request, 'chamados/chamado_sucesso.html', contexto)

def consultar_chamado_view(request):
    chamados_encontrados = None
    email_buscado = None
    form = ConsultaChamadoForm()
    if request.user.is_authenticated:
        email_buscado = request.user.email
    elif 'email_solicitante' in request.session:
        email_buscado = request.session.get('email_solicitante')
    if request.method == 'POST':
        form_post = ConsultaChamadoForm(request.POST)
        if form_post.is_valid():
            email_buscado = form_post.cleaned_data['email_solicitante']
            request.session['email_solicitante'] = email_buscado
        form = form_post
    if email_buscado:
        chamados_encontrados = Chamado.objects.filter(email_solicitante__iexact=email_buscado).order_by('-data_abertura')
        if not request.POST:
             form = ConsultaChamadoForm(initial={'email_solicitante': email_buscado})
    contexto = {'form': form, 'chamados_encontrados': chamados_encontrados, 'email_buscado': email_buscado}
    return render(request, 'chamados/consultar_chamado.html', contexto)

def chamado_detalhe_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    pode_comentar = False
    if request.user.is_authenticated and request.user.email.lower() == chamado.email_solicitante.lower():
        pode_comentar = True
    else:
        email_na_sessao = request.session.get('email_solicitante')
        if email_na_sessao and email_na_sessao.lower() == chamado.email_solicitante.lower():
            pode_comentar = True
    
    form_avaliacao = None
    form_reabertura = None
    if chamado.status == 'CONCLUIDO' and pode_comentar:
        form_avaliacao = AvaliacaoForm(instance=chamado)
        form_reabertura = ReaberturaForm()
            
    if request.method == 'POST' and pode_comentar and 'enviar_interacao' in request.POST:
        form_interacao = InteracaoForm(request.POST)
        if form_interacao.is_valid():
            nova_interacao = form_interacao.save(commit=False)
            nova_interacao.chamado = chamado
            chamado.save()
            nova_interacao.save()
            return redirect('chamado_detalhe', chamado_id=chamado.id)
    
    form_interacao = InteracaoForm()
    contexto = {
        'chamado': chamado,
        'form_interacao': form_interacao,
        'pode_comentar': pode_comentar,
        'form_avaliacao': form_avaliacao,
        'form_reabertura': form_reabertura,
    }
    return render(request, 'chamados/chamado_detalhe.html', contexto)

def avaliar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    if request.method == 'POST':
        form = AvaliacaoForm(request.POST, instance=chamado)
        if form.is_valid():
            form.save()
            chamado.status = 'ARQUIVADO'
            chamado.save()
    return redirect('chamado_detalhe', chamado_id=chamado.id)

def reabrir_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    if request.method == 'POST':
        form = ReaberturaForm(request.POST)
        if form.is_valid():
            motivo = form.cleaned_data['motivo']
            Interacao.objects.create(
                chamado=chamado,
                usuario=None,
                mensagem=f"Chamado reaberto pelo solicitante. Motivo: {motivo}"
            )
            chamado.status = 'PENDENTE'
            chamado.save()
    return redirect('chamado_detalhe', chamado_id=chamado.id)

@login_required
def editar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    usuario_logado = request.user
    is_coordenador = usuario_logado.groups.filter(name='Coordenadores').exists()
    is_tecnico_responsavel = (chamado.tecnico_responsavel == usuario_logado)
    if not (is_coordenador or is_tecnico_responsavel):
        raise PermissionDenied
    form_edicao = ChamadoUpdateForm(instance=chamado, user=usuario_logado)
    form_interacao = InteracaoForm()
    if request.method == 'POST':
        if 'salvar_edicao' in request.POST:
            form_edicao = ChamadoUpdateForm(request.POST, instance=chamado, user=usuario_logado)
            if form_edicao.is_valid():
                tecnico_anterior = chamado.tecnico_responsavel
                chamado_atualizado = form_edicao.save(commit=False)
                if is_coordenador and tecnico_anterior is None and chamado_atualizado.tecnico_responsavel is not None and chamado.status == 'ABERTA':
                    chamado_atualizado.status = 'EM_ANALISE'
                chamado_atualizado.save()
                return redirect('painel')
        elif 'enviar_interacao' in request.POST:
            form_interacao = InteracaoForm(request.POST)
            if form_interacao.is_valid():
                nova_interacao = form_interacao.save(commit=False)
                nova_interacao.chamado = chamado
                nova_interacao.usuario = usuario_logado
                nova_interacao.save()
                chamado.save()
                return redirect('editar_chamado', chamado_id=chamado.id)
    contexto = {'form_edicao': form_edicao, 'form_interacao': form_interacao, 'chamado': chamado}
    return render(request, 'chamados/editar_chamado.html', contexto)

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
                chamado.status = 'EM_ANALISE'
            chamado.save()
    return redirect('painel_coordenador')

@login_required
def iniciar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    chamado.status = 'EM_EXECUCAO'
    chamado.save()
    return redirect('painel')

@login_required
def finalizar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    chamado.status = 'CONCLUIDO'
    chamado.save()
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
    return redirect('painel')

def get_salas_por_bloco(request, bloco_id):
    salas = Sala.objects.filter(bloco_id=bloco_id).order_by('nome')
    salas_list = list(salas.values('id', 'nome'))
    return JsonResponse({'salas': salas_list})

def get_ativos_por_sala(request, sala_id):
    ativos = Ativo.objects.filter(localizacao_id=sala_id).order_by('nome')
    ativos_list = list(ativos.values('id', 'nome'))
    return JsonResponse({'ativos': ativos_list})

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
    chamados = Chamado.objects.all()
    filter_form = ChamadoFilterForm(request.GET)
    atribuicao_form = AtribuicaoTecnicoForm()
    pendencia_form = PendenciaForm()
    if filter_form.is_valid():
        status = filter_form.cleaned_data.get('status')
        tecnico = filter_form.cleaned_data.get('tecnico_responsavel')
        incluir_arquivados = filter_form.cleaned_data.get('incluir_arquivados')
        if not incluir_arquivados:
            chamados = chamados.exclude(status='ARQUIVADO')
        if status:
            chamados = chamados.filter(status=status)
        if tecnico:
            chamados = chamados.filter(tecnico_responsavel=tecnico)
    else:
        chamados = chamados.exclude(status='ARQUIVADO')
    chamados = chamados.order_by('data_abertura')
    contexto = {'chamados': chamados, 'titulo_pagina': titulo_pagina, 'filter_form': filter_form, 'atribuicao_form': atribuicao_form, 'pendencia_form': pendencia_form}
    return render(request, 'chamados/painel_coordenador.html', contexto)

@login_required
def painel_tecnico_view(request):
    if not request.user.groups.filter(name='Técnicos').exists():
        raise PermissionDenied
    titulo_pagina = "Meus Chamados Atribuídos"
    chamados = Chamado.objects.filter(tecnico_responsavel=request.user).exclude(status='ARQUIVADO').order_by('data_abertura')
    pendencia_form = PendenciaForm()
    contexto = {'chamados': chamados, 'titulo_pagina': titulo_pagina, 'pendencia_form': pendencia_form}
    return render(request, 'chamados/painel_tecnico.html', contexto)