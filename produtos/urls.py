from rest_framework.routers import SimpleRouter
from .views import ProdutoViewSet, FornecedorViewSet

router = SimpleRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'fornecedores', FornecedorViewSet)

urlpatterns = router.urls
