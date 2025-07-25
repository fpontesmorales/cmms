from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from ..forms import (
    ChamadoForm, ConsultaChamadoForm, InteracaoForm, AvaliacaoForm, 
    ReaberturaForm, PublicChamadoFilterForm
)
from ..models import Chamado, Interacao
from .. import emails

def homepage_view(request):
    return render(request, 'chamados/homepage.html')

def abrir_chamado_view(request):
    if request.method == 'POST':
        form = ChamadoForm(request.POST, request.FILES)
        if form.is_valid():
            novo_chamado = form.save()
            request.session['email_solicitante'] = novo_chamado.email_solicitante
            emails.enviar_email_novo_chamado(novo_chamado, request)
            emails.enviar_email_novo_chamado_admin(novo_chamado, request)
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
    
    if request.user.is_authenticated:
        email_buscado = request.user.email
    elif 'email_solicitante' in request.session:
        email_buscado = request.session.get('email_solicitante')
    
    form_email = ConsultaChamadoForm(request.POST or None, initial={'email_solicitante': email_buscado})

    if request.method == 'POST':
        if form_email.is_valid():
            email_buscado = form_email.cleaned_data['email_solicitante']
            request.session['email_solicitante'] = email_buscado
            
    filter_form = PublicChamadoFilterForm(request.GET, initial={'status': request.GET.get('status', '')})
    
    if email_buscado:
        lista_chamados = Chamado.objects.filter(email_solicitante__iexact=email_buscado).order_by('-data_modificacao')
        if filter_form.is_valid():
            status_filtrado = filter_form.cleaned_data.get('status')
            if status_filtrado:
                lista_chamados = lista_chamados.filter(status=status_filtrado)
        
        paginator = Paginator(lista_chamados, 10)
        page_number = request.GET.get('page')
        chamados_encontrados = paginator.get_page(page_number)
    
    contexto = {
        'form_email': form_email,
        'filter_form': filter_form,
        'chamados_encontrados': chamados_encontrados,
        'email_buscado': email_buscado,
    }
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
            emails.enviar_email_nova_interacao(nova_interacao, request)
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