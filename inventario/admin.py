from django.contrib import admin
from .models import TipoAtivo, Ativo

@admin.register(TipoAtivo)
class TipoAtivoAdmin(admin.ModelAdmin):
    """
    Configuração da exibição de Tipos de Ativo no admin.
    """
    search_fields = ('nome',)
    ordering = ('nome',)

@admin.register(Ativo)
class AtivoAdmin(admin.ModelAdmin):
    """
    Configuração da exibição de Ativos no admin com filtros e buscas úteis.
    """
    list_display = ('nome', 'codigo_patrimonio', 'tipo_ativo', 'localizacao', 'status')
    list_filter = ('status', 'tipo_ativo', 'localizacao__bloco')
    search_fields = ('nome', 'codigo_patrimonio', 'marca', 'modelo', 'localizacao__nome')
    ordering = ('nome',)