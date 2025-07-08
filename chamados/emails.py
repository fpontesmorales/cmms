import os
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.models import User
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def _enviar(assunto, contexto, template_html, email_destinatario):
    try:
        # PONTO DE DIAGNÓSTICO 2
        print(f"--- Dentro de _enviar. Tentando enviar '{assunto}' para {email_destinatario} ---")

        corpo_html = render_to_string(template_html, contexto)
        
        if settings.DEBUG:
            print("--- MODO DE DESENVOLVIMENTO: E-MAIL SIMULADO ---")
            print(f"PARA: {email_destinatario}")
            print(f"ASSUNTO: {assunto}")
            print("--- CORPO DO E-MAIL (início) ---")
            print(corpo_html[:300] + "...") # Imprime apenas o início para não poluir
            print("--- CORPO DO E-MAIL (fim) ---")
            return

        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            print("ERRO DE ENVIO: Chave da API do SendGrid não configurada.")
            return

        message = Mail(
            from_email=('infra.caucaia@ifce.edu.br', 'CMMS Infra IFCE Caucaia'),
            to_emails=email_destinatario,
            subject=assunto,
            html_content=corpo_html
        )
        sendgrid_client = SendGridAPIClient(api_key)
        response = sendgrid_client.send(message)
        print(f"E-mail '{assunto}' enviado para {email_destinatario}. Status: {response.status_code}")

    except Exception as e:
        print(f"ERRO AO TENTAR ENVIAR E-MAIL: {e}")


def enviar_email_novo_chamado(chamado, request):
    assunto = f"Confirmação de Abertura de Chamado #{chamado.id}"
    template = 'emails/confirmacao_chamado.html'
    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[chamado.id]))
    contexto_email = {'chamado': chamado, 'url_detalhe': url_detalhe}
    _enviar(assunto, contexto_email, template, chamado.email_solicitante)


def enviar_email_status_alterado(chamado, request):
    assunto = f"Atualização do seu Chamado #{chamado.id}: {chamado.get_status_display()}"
    template = 'emails/status_alterado.html'
    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[chamado.id]))
    contexto_email = {'chamado': chamado, 'url_detalhe': url_detalhe}
    _enviar(assunto, contexto_email, template, chamado.email_solicitante)


def enviar_email_nova_interacao(interacao, request):
    chamado = interacao.chamado
    assunto = f"Nova Mensagem no seu Chamado #{chamado.id}"
    template = 'emails/nova_interacao.html'
    url_detalhe = request.build_absolute_uri(reverse('chamado_detalhe', args=[chamado.id]))
    contexto_email = {'chamado': chamado, 'interacao': interacao, 'url_detalhe': url_detalhe}
    _enviar(assunto, contexto_email, template, chamado.email_solicitante)


def enviar_email_atribuicao_tecnico(chamado, request):
    tecnico = chamado.tecnico_responsavel
    if not tecnico or not tecnico.email:
        return
    assunto = f"Novo Chamado Atribuído a Você: #{chamado.id}"
    template = 'emails/notificacao_atribuicao.html'
    url_painel = request.build_absolute_uri(reverse('painel'))
    contexto_email = {'chamado': chamado, 'tecnico': tecnico, 'url_painel': url_painel}
    _enviar(assunto, contexto_email, template, tecnico.email)


def enviar_email_novo_chamado_admin(chamado, request):
    assunto = f"Novo Chamado Aberto no Sistema: #{chamado.id} - {chamado.tipo_servico.nome}"
    template = 'emails/notificacao_novo_chamado_admin.html'
    url_painel = request.build_absolute_uri(reverse('painel'))
    contexto_email = {'chamado': chamado, 'url_painel': url_painel}
    
    coordenadores = User.objects.filter(groups__name='Coordenadores')
    lista_emails_destinatarios = [user.email for user in coordenadores if user.email]
    
    # PONTO DE DIAGNÓSTICO 3
    print(f">>> Buscando coordenadores para notificar. Encontrados: {lista_emails_destinatarios}")
    
    if lista_emails_destinatarios:
        _enviar(assunto, contexto_email, template, lista_emails_destinatarios)
    else:
        print(">>> AVISO: Nenhum coordenador com e-mail cadastrado foi encontrado para notificar.")