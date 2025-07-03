from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cadastros.models import Bloco, Sala, TipoServico
from inventario.models import Ativo

class Chamado(models.Model):
    STATUS_CHOICES = [
        ('ABERTA', 'Aberta'),
        ('EM_ANALISE', 'Em Análise'),
        ('PENDENTE', 'Pendente'),
        ('EM_EXECUCAO', 'Em Execução'),
        ('CONCLUIDO', 'Concluído'),
        ('ARQUIVADO', 'Arquivado'),
    ]

    email_solicitante = models.EmailField(max_length=255, verbose_name="E-mail do Solicitante")
    bloco = models.ForeignKey('cadastros.Bloco', on_delete=models.PROTECT, verbose_name="Bloco do Serviço")
    sala = models.ForeignKey('cadastros.Sala', on_delete=models.PROTECT, verbose_name="Sala do Serviço")
    tipo_servico = models.ForeignKey('cadastros.TipoServico', on_delete=models.PROTECT, verbose_name="Tipo de Serviço")
    ativo = models.ForeignKey('inventario.Ativo', on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Ativo Específico (Opcional)")
    descricao = models.TextField(verbose_name="Descrição Detalhada do Serviço")
    foto = models.ImageField(upload_to='fotos_chamados/', blank=True, null=True, verbose_name="Foto")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ABERTA', verbose_name="Status")
    data_abertura = models.DateTimeField(auto_now_add=True, verbose_name="Data de Abertura")
    data_modificacao = models.DateTimeField(auto_now=True, verbose_name="Última Modificação")
    
    observacoes_tecnicas = models.TextField(blank=True, null=True, verbose_name="Observações Técnicas")
    data_visita = models.DateField(blank=True, null=True, verbose_name="Data da Visita Agendada")
    tecnico_responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Técnico Responsável")
    avaliacao = models.IntegerField(blank=True, null=True, verbose_name="Avaliação (1-5)")
    comentario_avaliacao = models.TextField(blank=True, null=True, verbose_name="Comentário da Avaliação")
    
    def __str__(self):
        return f"Chamado #{self.id} - {self.tipo_servico.nome} em {self.sala}"

class Interacao(models.Model):
    chamado = models.ForeignKey(Chamado, on_delete=models.CASCADE, related_name='interacoes', verbose_name="Chamado")
    mensagem = models.TextField(verbose_name="Mensagem")
    data_interacao = models.DateTimeField(auto_now_add=True, verbose_name="Data")
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="Usuário Interno")

    class Meta:
        verbose_name = "Interação"
        verbose_name_plural = "Interações"
        ordering = ['data_interacao']

    def __str__(self):
        autor = self.usuario.username if self.usuario else "Solicitante"
        return f"Mensagem de {autor} no chamado #{self.chamado.id} em {self.data_interacao.strftime('%d/%m/%Y')}"