from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # A rota 'chamados/' foi movida para o final por uma questão de ordem lógica
    # mas a principal mudança é que não há a rota 'painel/' aqui.
    path('', include('chamados.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)