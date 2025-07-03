from django.db import models
from cadastros.models import Sala

class TipoAtivo(models.Model):
    """
    Define a categoria de um ativo.
    Ex: Climatização, Mobiliário, Equipamento de TI.
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Tipo")

    class Meta:
        verbose_name = "Tipo de Ativo"
        verbose_name_plural = "Tipos de Ativos"
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Ativo(models.Model):
    """
    Representa um equipamento físico individual no campus.
    """
    STATUS_CHOICES = [
        ('OPERACAO', 'Em Operação'),
        ('MANUTENCAO', 'Em Manutenção'),
        ('INATIVO', 'Fora de Operação'),
    ]

    nome = models.CharField(max_length=255, verbose_name="Nome/Descrição do Ativo")
    codigo_patrimonio = models.CharField(max_length=100, unique=True, verbose_name="Tombo")
    tipo_ativo = models.ForeignKey(TipoAtivo, on_delete=models.PROTECT, verbose_name="Tipo de Ativo")
    localizacao = models.ForeignKey(Sala, on_delete=models.PROTECT, verbose_name="Localização (Sala)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPERACAO', verbose_name="Status")
    marca = models.CharField(max_length=100, blank=True, verbose_name="Marca")
    modelo = models.CharField(max_length=100, blank=True, verbose_name="Modelo")
    
    class Meta:
        verbose_name = "Ativo"
        verbose_name_plural = "Ativos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.codigo_patrimonio})"