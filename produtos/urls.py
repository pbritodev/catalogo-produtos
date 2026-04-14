from rest_framework.routers import DefaultRouter
from .views import ProdutoViewSet, FornecedorViewSet

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'fornecedores', FornecedorViewSet)

urlpatterns = router.urls