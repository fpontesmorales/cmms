from django.contrib import admin
from .models import Chamado, Interacao

class InteracaoInline(admin.TabularInline):
    model = Interacao
    extra = 1
    readonly_fields = ('data_interacao',)
    exclude = ('usuario',)

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'sala', 'tipo_servico', 'status', 'tecnico_responsavel', 'data_abertura')
    list_filter = ('status', 'tipo_servico', 'tecnico_responsavel')
    search_fields = ('id', 'descricao', 'sala__nome', 'sala__bloco__nome')
    date_hierarchy = 'data_abertura'
    ordering = ('-data_abertura',)
    inlines = [InteracaoInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, Interacao) and not instance.pk:
                instance.usuario = request.user
            instance.save()
        formset.save_m2m()

@admin.register(Interacao)
class InteracaoAdmin(admin.ModelAdmin):
    list_display = ('chamado', 'usuario_display', 'data_interacao_formatada')
    list_filter = ('chamado', 'usuario')
    search_fields = ('mensagem',)
    
    def usuario_display(self, obj):
        return obj.usuario.username if obj.usuario else "Solicitante"
    usuario_display.short_description = "Autor"

    def data_interacao_formatada(self, obj):
        return obj.data_interacao.strftime("%d/%m/%Y %H:%M")
    data_interacao_formatada.short_description = "Data"