import os
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def _enviar_email_real(assunto, corpo_html, email_destinatario, nome_remetente='CMMS Infra IFCE Caucaia'):
    """
    Função interna que monta e dispara um e-mail real usando a API do SendGrid.
    """
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        print("ERRO DE PRODUÇÃO: Chave da API do SendGrid não configurada.")
        return

    message = Mail(
        from_email=(settings.DEFAULT_FROM_EMAIL, nome_remetente),
        to_emails=email_destinatario,
        subject=assunto,
        html_content=corpo_html
    )
    
    try:
        sendgrid_client = SendGridAPIClient(api_key)
        response = sendgrid_client.send(message)
        print(f"E-mail '{assunto}' enviado para {email_destinatario} via SendGrid. Status: {response.status_code}")
    except Exception as e:
        print(f"ERRO AO ENVIAR E-MAIL VIA SENDGRID: {e}")

def _simular_email_console(assunto, corpo_html, email_destinatario):
    """
    Função interna que simula o envio de e-mail imprimindo no console.
    """
    print("\n" + "="*50)
    print("--- MODO DE DESENVOLVIMENTO: E-MAIL SIMULADO ---")
    print(f"DE: {settings.DEFAULT_FROM_EMAIL}")
    print(f"PARA: {email_destinatario}")
    print(f"ASSUNTO: {assunto}")
    print("--- CORPO DO E-MAIL ---")
    # Imprime apenas o início para não poluir o terminal
    print(corpo_html.strip()[:500] + "...")
    print("="*50 + "\n")

def enviar_email_novo_chamado(chamado, request):
    assunto = f"Confirmação de Abertura de Chamado #{chamado.id}"
    template = 'emails/confirmacao_chamado.html'
    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[chamado.id]))
    contexto = {'chamado': chamado, 'url_detalhe': url_detalhe}
    corpo_html = render_to_string(template, contexto)
    
    if settings.DEBUG:
        _simular_email_console(assunto, corpo_html, chamado.email_solicitante)
    else:
        _enviar_email_real(assunto, corpo_html, chamado.email_solicitante)

def enviar_email_novo_chamado_admin(chamado, request):
    assunto = f"Novo Chamado no Sistema: #{chamado.id}"
    template = 'emails/notificacao_novo_chamado_admin.html'
    url_painel = request.build_absolute_uri(reverse('painel'))
    contexto = {'chamado': chamado, 'url_painel': url_painel}
    corpo_html = render_to_string(template, contexto)

    coordenadores = User.objects.filter(groups__name='Coordenadores', email__isnull=False).exclude(email='')
    lista_emails = [user.email for user in coordenadores]

    if lista_emails:
        if settings.DEBUG:
            _simular_email_console(assunto, corpo_html, lista_emails)
        else:
            _enviar_email_real(assunto, corpo_html, lista_emails)

def enviar_email_atribuicao_tecnico(chamado, request):
    tecnico = chamado.tecnico_responsavel
    if not tecnico or not tecnico.email:
        return
        
    assunto = f"Novo Chamado Atribuído a Você: #{chamado.id}"
    template = 'emails/notificacao_atribuicao.html'
    url_painel = request.build_absolute_uri(reverse('painel'))
    contexto = {'chamado': chamado, 'tecnico': tecnico, 'url_painel': url_painel}
    corpo_html = render_to_string(template, contexto)

    if settings.DEBUG:
        _simular_email_console(assunto, corpo_html, tecnico.email)
    else:
        _enviar_email_real(assunto, corpo_html, tecnico.email)

def enviar_email_status_alterado(chamado, request):
    assunto = f"Atualização do seu Chamado #{chamado.id}: {chamado.get_status_display()}"
    template = 'emails/status_alterado.html'
    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[chamado.id]))
    contexto = {'chamado': chamado, 'url_detalhe': url_detalhe}
    corpo_html = render_to_string(template, contexto)
    
    if settings.DEBUG:
        _simular_email_console(assunto, corpo_html, chamado.email_solicitante)
    else:
        _enviar_email_real(assunto, corpo_html, chamado.email_solicitante)

def enviar_email_nova_interacao(interacao, request):
    chamado = interacao.chamado
    assunto = f"Nova Mensagem no seu Chamado #{chamado.id}"
    template = 'emails/nova_interacao.html'
    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[chamado.id]))
    contexto = {'chamado': chamado, 'interacao': interacao, 'url_detalhe': url_detalhe}
    corpo_html = render_to_string(template, contexto)

    if settings.DEBUG:
        _simular_email_console(assunto, corpo_html, chamado.email_solicitante)
    else:
        _enviar_email_real(assunto, corpo_html, chamado.email_solicitante)