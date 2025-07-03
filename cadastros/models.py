from django.db import models

class Bloco(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome do Bloco")
    class Meta:
        verbose_name = "Bloco"
        verbose_name_plural = "Blocos"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class TipoPiso(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    class Meta:
        verbose_name = "Tipo de Piso"
        verbose_name_plural = "Tipos de Pisos"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class TipoForro(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    class Meta:
        verbose_name = "Tipo de Forro"
        verbose_name_plural = "Tipos de Forro"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class TipoPintura(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    class Meta:
        verbose_name = "Tipo de Pintura"
        verbose_name_plural = "Tipos de Pintura"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class TipoPorta(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome")
    class Meta:
        verbose_name = "Tipo de Porta"
        verbose_name_plural = "Tipos de Porta"
        ordering = ['nome']
    def __str__(self):
        return self.nome

class Sala(models.Model):
    nome = models.CharField(max_length=100, verbose_name="Nome/Número da Sala")
    bloco = models.ForeignKey(Bloco, on_delete=models.CASCADE, verbose_name="Bloco")
    metragem = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name="Metragem (m²)")
    tipo_piso = models.ForeignKey(TipoPiso, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Tipo de Piso")
    tipo_forro = models.ForeignKey(TipoForro, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Tipo de Forro")
    tipo_pintura = models.ForeignKey(TipoPintura, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Tipo de Pintura")
    tipo_porta = models.ForeignKey(TipoPorta, on_delete=models.PROTECT, blank=True, null=True, verbose_name="Tipo de Porta")
    qtd_luminarias = models.PositiveIntegerField(blank=True, null=True, verbose_name="Quantidade de Luminárias")
    qtd_tomadas = models.PositiveIntegerField(blank=True, null=True, verbose_name="Quantidade de Tomadas")
    qtd_interruptores = models.PositiveIntegerField(blank=True, null=True, verbose_name="Quantidade de Interruptores")
    class Meta:
        verbose_name = "Sala"
        verbose_name_plural = "Salas"
        unique_together = ['bloco', 'nome']
        ordering = ['bloco__nome', 'nome']
    def __str__(self):
        return f"{self.bloco.nome} - {self.nome}"

class TipoServico(models.Model):
    nome = models.CharField(max_length=255, unique=True, verbose_name="Tipo de Serviço")
    class Meta:
        verbose_name = "Tipo de Serviço"
        verbose_name_plural = "Tipos de Serviço"
        ordering = ['nome']
    def __str__(self):
        return self.nome