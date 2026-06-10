from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Cliente, Pedido, ItemPedido, Carrinho, ItemCarrinho
from .serializers import (
    ClienteSerializer,
    PedidoSerializer,
    PedidoCriarSerializer,
    AtualizarStatusSerializer,
    CarrinhoSerializer,
    AdicionarItemCarrinhoSerializer,
    CheckoutSerializer,
)


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.filter(ativo=True)
    serializer_class = ClienteSerializer


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.prefetch_related('itens__produto').select_related('cliente')
    serializer_class = PedidoSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PedidoCriarSerializer
        return PedidoSerializer

    def create(self, request, *args, **kwargs):
        serializer = PedidoCriarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido = serializer.save()
        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['patch'], url_path='status')
    def atualizar_status(self, request, pk=None):
        pedido = self.get_object()
        serializer = AtualizarStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pedido.status = serializer.validated_data['status']
        pedido.save()
        return Response(PedidoSerializer(pedido).data)

    @action(detail=False, methods=['get'], url_path='por-cliente/(?P<cliente_id>[^/.]+)')
    def por_cliente(self, request, cliente_id=None):
        pedidos = Pedido.objects.filter(cliente_id=cliente_id).prefetch_related('itens__produto')
        serializer = PedidoSerializer(pedidos, many=True)
        return Response(serializer.data)


class CarrinhoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    Operações do carrinho de compras.

    GET    /carrinhos/                  → listar carrinhos em aberto
    GET    /carrinhos/{id}/             → ver carrinho
    POST   /carrinhos/{id}/adicionar/   → adicionar/atualizar item
    DELETE /carrinhos/{id}/remover/     → remover item
    POST   /carrinhos/{id}/checkout/    → converter em pedido
    DELETE /carrinhos/{id}/limpar/      → esvaziar carrinho
    POST   /carrinhos/                  → criar novo carrinho
    """
    queryset = Carrinho.objects.prefetch_related('itens__produto').select_related('cliente')
    serializer_class = CarrinhoSerializer

    def get_queryset(self):
        qs = Carrinho.objects.prefetch_related('itens__produto').select_related('cliente')
        # ?abertos=true → apenas carrinhos que possuem itens (em aberto)
        if self.request.query_params.get('abertos') in ('true', '1'):
            qs = qs.filter(itens__isnull=False).distinct()
        return qs.order_by('-atualizado_em')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        carrinho = get_object_or_404(
            Carrinho.objects.prefetch_related('itens__produto'), pk=pk
        )
        return Response(CarrinhoSerializer(carrinho).data)

    def create(self, request):
        cliente_id = request.data.get('cliente_id')
        sessao_id = request.data.get('sessao_id', '')

        if cliente_id:
            carrinho, _ = Carrinho.objects.get_or_create(cliente_id=cliente_id)
        else:
            if not sessao_id:
                return Response(
                    {'detail': 'Informe cliente_id ou sessao_id.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            carrinho, _ = Carrinho.objects.get_or_create(sessao_id=sessao_id)

        return Response(CarrinhoSerializer(carrinho).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='adicionar')
    def adicionar(self, request, pk=None):
        carrinho = get_object_or_404(Carrinho, pk=pk)
        serializer = AdicionarItemCarrinhoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        from produtos.models import Produto
        produto = get_object_or_404(Produto, pk=serializer.validated_data['produto_id'])
        quantidade = serializer.validated_data['quantidade']

        item, created = ItemCarrinho.objects.get_or_create(
            carrinho=carrinho,
            produto=produto,
            defaults={'quantidade': quantidade}
        )
        if not created:
            item.quantidade += quantidade
            item.save()

        return Response(CarrinhoSerializer(carrinho).data)

    @action(detail=True, methods=['delete'], url_path='remover/(?P<item_id>[^/.]+)')
    def remover(self, request, pk=None, item_id=None):
        carrinho = get_object_or_404(Carrinho, pk=pk)
        item = get_object_or_404(ItemCarrinho, pk=item_id, carrinho=carrinho)
        item.delete()
        return Response(CarrinhoSerializer(carrinho).data)

    @action(detail=True, methods=['delete'], url_path='limpar')
    def limpar(self, request, pk=None):
        carrinho = get_object_or_404(Carrinho, pk=pk)
        carrinho.itens.all().delete()
        return Response(CarrinhoSerializer(carrinho).data)

    @action(detail=True, methods=['post'], url_path='checkout')
    def checkout(self, request, pk=None):
        carrinho = get_object_or_404(Carrinho.objects.prefetch_related('itens'), pk=pk)
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pedido = carrinho.converter_em_pedido(**serializer.validated_data)
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            PedidoSerializer(pedido).data,
            status=status.HTTP_201_CREATED
        )
