from django.urls import path
from . import views

urlpatterns = [
    path('', views.abrir_chamado_view, name='abrir_chamado'),
    path('painel/', views.painel_view, name='painel'),
    path('painel/chamado/<int:chamado_id>/editar/', views.editar_chamado_view, name='editar_chamado'),
    path('sucesso/<int:chamado_id>/', views.chamado_sucesso_view, name='chamado_sucesso'),
    path('consultar/', views.consultar_chamado_view, name='consultar_chamado'),
    path('detalhe/<int:chamado_id>/', views.chamado_detalhe_view, name='chamado_detalhe'),
    path('api/get-salas/<int:bloco_id>/', views.get_salas_por_bloco, name='get_salas_por_bloco'),
    path('api/get-ativos/<int:sala_id>/', views.get_ativos_por_sala, name='get_ativos_por_sala'),
]