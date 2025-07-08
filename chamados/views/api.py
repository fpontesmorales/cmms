from django.http import JsonResponse
from cadastros.models import Sala
from inventario.models import Ativo

def get_salas_por_bloco(request, bloco_id):
    salas = Sala.objects.filter(bloco_id=bloco_id).order_by('nome')
    salas_list = list(salas.values('id', 'nome'))
    return JsonResponse({'salas': salas_list})

def get_ativos_por_sala(request, sala_id):
    ativos = Ativo.objects.filter(localizacao_id=sala_id).order_by('nome')
    ativos_list = list(ativos.values('id', 'nome'))
    return JsonResponse({'ativos': ativos_list})