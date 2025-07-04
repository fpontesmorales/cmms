from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('abrir-chamado/', views.abrir_chamado_view, name='abrir_chamado'),
    path('painel/', views.painel_view, name='painel'),
    path('painel/coordenador/', views.painel_coordenador_view, name='painel_coordenador'),
    path('painel/tecnico/', views.painel_tecnico_view, name='painel_tecnico'),
    path('painel/chamado/<int:chamado_id>/editar/', views.editar_chamado_view, name='editar_chamado'),
    path('painel/chamado/<int:chamado_id>/atribuir/', views.atribuir_tecnico_view, name='atribuir_tecnico'),
    path('chamado/<int:chamado_id>/iniciar/', views.iniciar_chamado_view, name='iniciar_chamado'),
    path('chamado/<int:chamado_id>/finalizar/', views.finalizar_chamado_view, name='finalizar_chamado'),
    path('chamado/<int:chamado_id>/pendente/', views.pendente_chamado_view, name='pendente_chamado'),
    path('chamado/<int:chamado_id>/avaliar/', views.avaliar_chamado_view, name='avaliar_chamado'),
    path('chamado/<int:chamado_id>/reabrir/', views.reabrir_chamado_view, name='reabrir_chamado'),
    path('sucesso/<int:chamado_id>/', views.chamado_sucesso_view, name='chamado_sucesso'),
    path('consultar/', views.consultar_chamado_view, name='consultar_chamado'),
    path('detalhe/<int:chamado_id>/', views.chamado_detalhe_view, name='chamado_detalhe'),
    path('api/get-salas/<int:bloco_id>/', views.get_salas_por_bloco, name='get_salas_por_bloco'),
    path('api/get-ativos/<int:sala_id>/', views.get_ativos_por_sala, name='get_ativos_por_sala'),
]