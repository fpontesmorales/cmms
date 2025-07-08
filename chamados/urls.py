from django.urls import path
from .views import (
    homepage_view, 
    abrir_chamado_view, 
    chamado_sucesso_view,
    consultar_chamado_view, 
    chamado_detalhe_view,
    painel_view,
    painel_coordenador_view,
    painel_tecnico_view,
    editar_chamado_view,
    atribuir_tecnico_view,
    iniciar_analise_view,
    iniciar_execucao_view,
    finalizar_chamado_view,
    pendente_chamado_view,
    cancelar_chamado_view,
    avaliar_chamado_view,
    reabrir_chamado_view,
    get_salas_por_bloco,
    get_ativos_por_sala
)

urlpatterns = [
    # Rotas Públicas
    path('', homepage_view, name='homepage'),
    path('abrir-chamado/', abrir_chamado_view, name='abrir_chamado'),
    path('sucesso/<int:chamado_id>/', chamado_sucesso_view, name='chamado_sucesso'),
    path('consultar/', consultar_chamado_view, name='consultar_chamado'),
    path('detalhe/<int:chamado_id>/', chamado_detalhe_view, name='chamado_detalhe'),
    
    # Rotas do Painel da Equipe
    path('painel/', painel_view, name='painel'),
    path('painel/coordenador/', painel_coordenador_view, name='painel_coordenador'),
    path('painel/tecnico/', painel_tecnico_view, name='painel_tecnico'),
    path('painel/chamado/<int:chamado_id>/editar/', editar_chamado_view, name='editar_chamado'),
    
    # Rotas de Ações (disparadas por botões)
    path('painel/chamado/<int:chamado_id>/atribuir/', atribuir_tecnico_view, name='atribuir_tecnico'),
    path('chamado/<int:chamado_id>/iniciar_analise/', iniciar_analise_view, name='iniciar_analise'),
    path('chamado/<int:chamado_id>/iniciar_execucao/', iniciar_execucao_view, name='iniciar_execucao'),
    path('chamado/<int:chamado_id>/finalizar/', finalizar_chamado_view, name='finalizar_chamado'),
    path('chamado/<int:chamado_id>/pendente/', pendente_chamado_view, name='pendente_chamado'),
    path('chamado/<int:chamado_id>/cancelar/', cancelar_chamado_view, name='cancelar_chamado'),
    path('chamado/<int:chamado_id>/avaliar/', avaliar_chamado_view, name='avaliar_chamado'),
    path('chamado/<int:chamado_id>/reabrir/', reabrir_chamado_view, name='reabrir_chamado'),
    
    # Rotas da API de dados para o JavaScript
    path('api/get-salas/<int:bloco_id>/', get_salas_por_bloco, name='get_salas_por_bloco'),
    path('api/get-ativos/<int:sala_id>/', get_ativos_por_sala, name='get_ativos_por_sala'),
]