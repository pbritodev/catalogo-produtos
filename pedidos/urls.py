from rest_framework.routers import SimpleRouter
from .views import ClienteViewSet, PedidoViewSet, CarrinhoViewSet

router = SimpleRouter()
router.register(r'clientes', ClienteViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'carrinhos', CarrinhoViewSet)

urlpatterns = router.urls
