from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def healthcheck(_request):
    return JsonResponse({'status': 'ok'})


urlpatterns = [
    path('', include('loja.urls')),          # site (interface da loja) na raiz /
    path('health/', healthcheck),            # healthcheck para deploy
    path('admin/', admin.site.urls),

    # API REST com Browsable API do DRF em /api/
    path('api/', include('catalogo.api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
