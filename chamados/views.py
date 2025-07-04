import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from .forms import ChamadoForm, ConsultaChamadoForm, InteracaoForm, ChamadoUpdateForm, ChamadoFilterForm
from .models import Chamado, Interacao
from cadastros.models import Sala
from inventario.models import Ativo

def abrir_chamado_view(request):
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            novo_chamado = form.save()
            request.session['email_solicitante'] = novo_chamado.email_solicitante
            try:
                assunto = f"Confirmação de Abertura de Chamado #{novo_chamado.id}"
                url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[novo_chamado.id]))
                contexto_email = {'chamado': novo_chamado, 'url_detalhe': url_detalhe}
                corpo_html = render_to_string('emails/confirmacao_chamado.html', contexto_email)
                corpo_texto = f"Seu chamado #{novo_chamado.id} foi aberto com sucesso. Acompanhe em: {url_detalhe}"
                email_remetente = 'infra.caucaia@ifce.edu.br'
                email_destinatario = [novo_chamado.email_solicitante]
                send_mail(subject=assunto, message=corpo_texto, from_email=email_remetente, recipient_list=email_destinatario, html_message=corpo_html, fail_silently=False)
            except Exception as e:
                print(f"Erro ao tentar enviar e-mail de confirmação: {e}")
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
    api_key_vista_pela_view = os.environ.get('SENDGRID_API_KEY', '!!! CHAVE NÃO ENCONTRADA !!!')
    contexto = {
        'chamado': chamado,
        'api_key_debug': api_key_vista_pela_view
    }
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
    email_na_sessao = request.session.get('email_solicitante')
    pode_comentar = email_na_sessao and (email_na_sessao.lower() == chamado.email_solicitante.lower())
    if request.method == 'POST' and pode_comentar:
        form_interacao = InteracaoForm(request.POST)
        if form_interacao.is_valid():
            nova_interacao = form_interacao.save(commit=False)
            nova_interacao.chamado = chamado
            chamado.save()
            nova_interacao.save()
            return redirect('chamado_detalhe', chamado_id=chamado.id)
    form_interacao = InteracaoForm()
    contexto = {'chamado': chamado, 'form_interacao': form_interacao, 'pode_comentar': pode_comentar}
    return render(request, 'chamados/chamado_detalhe.html', contexto)

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
    chamados = None
    titulo_pagina = "Meu Painel"
    filter_form = ChamadoFilterForm(request.GET)
    if usuario_logado.groups.filter(name='Coordenadores').exists():
        titulo_pagina = "Painel do Coordenador"
        chamados = Chamado.objects.exclude(status='ARQUIVADO')
        if filter_form.is_valid():
            status = filter_form.cleaned_data.get('status')
            tecnico = filter_form.cleaned_data.get('tecnico_responsavel')
            if status:
                chamados = chamados.filter(status=status)
            if tecnico:
                chamados = chamados.filter(tecnico_responsavel=tecnico)
        chamados = chamados.order_by('data_abertura')
    elif usuario_logado.groups.filter(name='Técnicos').exists():
        titulo_pagina = "Meus Chamados Atribuídos"
        chamados = Chamado.objects.filter(tecnico_responsavel=usuario_logado).exclude(status='ARQUIVADO').order_by('data_abertura')
    contexto = {'chamados': chamados, 'titulo_pagina': titulo_pagina, 'filter_form': filter_form}
    return render(request, 'chamados/painel.html', contexto)

@login_required
def editar_chamado_view(request, chamado_id):
    chamado = get_object_or_404(Chamado, pk=chamado_id)
    usuario_logado = request.user
    is_coordenador = usuario_logado.groups.filter(name='Coordenadores').exists()
    is_tecnico_responsavel = (chamado.tecnico_responsavel == usuario_logado)
    if not (is_coordenador or is_tecnico_responsavel):
        raise PermissionDenied
    if request.method == 'POST':
        form = ChamadoUpdateForm(request.POST, instance=chamado)
        if form.is_valid():
            form.save()
            return redirect('painel')
    else:
        form = ChamadoUpdateForm(instance=chamado)
    contexto = {'form': form, 'chamado': chamado}
    return render(request, 'chamados/editar_chamado.html', contexto)