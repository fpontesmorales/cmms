from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.html import format_html
from .models import Bloco, Sala, TipoServico, TipoPiso, TipoForro, TipoPintura, TipoPorta, Funcao, PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil do Usuário'
    fk_name = 'usuario'

class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

class SalaInline(admin.TabularInline):
    model = Sala
    fields = ('nome',)
    extra = 1

@admin.register(Bloco)
class BlocoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ver_salas_link')
    inlines = [SalaInline]
    search_fields = ('nome',)
    ordering = ('nome',)

    def ver_salas_link(self, obj):
        contagem = obj.sala_set.count()
        url = (reverse("admin:cadastros_sala_changelist") + f"?bloco__id__exact={obj.id}")
        return format_html('<a href="{}">Ver {} Salas</a>', url, contagem)
    ver_salas_link.short_description = "Salas no Bloco"

@admin.register(Sala)
class SalaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'bloco', 'metragem', 'tipo_piso')
    list_filter = ('bloco', 'tipo_piso', 'tipo_forro')
    search_fields = ('nome',)
    fieldsets = (
        ('Informações Básicas', {'fields': ('bloco', 'nome')}),
        ('Características do Ambiente', {'fields': ('metragem', 'tipo_piso', 'tipo_forro', 'tipo_pintura', 'tipo_porta')}),
        ('Instalações Elétricas', {'fields': ('qtd_luminarias', 'qtd_tomadas', 'qtd_interruptores')}),
    )
    ordering = ('bloco__nome', 'nome')

# Re-registra o modelo User com nosso admin customizado
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Registra os outros modelos
admin.site.register(TipoServico)
admin.site.register(TipoPiso)
admin.site.register(TipoForro)
admin.site.register(TipoPintura)
admin.site.register(TipoPorta)
admin.site.register(Funcao)