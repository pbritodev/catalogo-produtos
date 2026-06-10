"""Roteador central da API REST (Browsable API do DRF).

Registra todos os viewsets num único DefaultRouter, de modo que /api/
exibe a API root navegável com links para todos os recursos.
"""
from rest_framework.routers import DefaultRouter

from produtos.views import ProdutoViewSet, FornecedorViewSet
from pedidos.views import ClienteViewSet, PedidoViewSet, CarrinhoViewSet

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'fornecedores', FornecedorViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'carrinhos', CarrinhoViewSet)

urlpatterns = router.urls
