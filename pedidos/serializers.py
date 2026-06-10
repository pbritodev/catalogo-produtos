from rest_framework import serializers
from .models import Cliente, Pedido, ItemPedido, Carrinho, ItemCarrinho
from produtos.serializers import ProdutoSerializer


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'


# ── Carrinho ──────────────────────────────────────────────────────────────────

class ItemCarrinhoSerializer(serializers.ModelSerializer):
    produto_detalhe = ProdutoSerializer(source='produto', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemCarrinho
        fields = ['id', 'produto', 'produto_detalhe', 'quantidade', 'subtotal']


class CarrinhoSerializer(serializers.ModelSerializer):
    itens = ItemCarrinhoSerializer(many=True, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    quantidade_itens = serializers.IntegerField(read_only=True)

    class Meta:
        model = Carrinho
        fields = ['id', 'cliente', 'sessao_id', 'itens', 'total', 'quantidade_itens', 'atualizado_em']


class AdicionarItemCarrinhoSerializer(serializers.Serializer):
    produto_id = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1, default=1)


class CheckoutSerializer(serializers.Serializer):
    forma_pagamento = serializers.ChoiceField(
        choices=Pedido.FormaPagamento.choices,
        required=False,
        default=''
    )
    observacoes = serializers.CharField(required=False, default='')


# ── Pedido ────────────────────────────────────────────────────────────────────

class ItemPedidoSerializer(serializers.ModelSerializer):
    produto_detalhe = ProdutoSerializer(source='produto', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = ItemPedido
        fields = [
            'id', 'produto', 'produto_detalhe',
            'quantidade', 'preco_unitario', 'desconto_item', 'subtotal',
        ]


class PedidoSerializer(serializers.ModelSerializer):
    itens = ItemPedidoSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    pagamento_display = serializers.CharField(source='get_forma_pagamento_display', read_only=True)
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'numero', 'cliente', 'cliente_nome',
            'status', 'status_display',
            'forma_pagamento', 'pagamento_display',
            'endereco_entrega', 'observacoes',
            'subtotal', 'desconto', 'frete', 'total',
            'data_pedido', 'data_atualizacao',
            'itens',
        ]
        read_only_fields = ['numero', 'subtotal', 'total', 'data_pedido', 'data_atualizacao']


class PedidoCriarSerializer(serializers.Serializer):
    """Cria pedido diretamente (sem passar pelo carrinho)."""

    class ItemInput(serializers.Serializer):
        produto_id = serializers.IntegerField()
        quantidade = serializers.IntegerField(min_value=1)
        preco_unitario = serializers.DecimalField(
            max_digits=10, decimal_places=2, required=False
        )

    cliente_id = serializers.IntegerField()
    forma_pagamento = serializers.ChoiceField(
        choices=Pedido.FormaPagamento.choices, required=False, default=''
    )
    endereco_entrega = serializers.CharField(required=False, default='')
    observacoes = serializers.CharField(required=False, default='')
    frete = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    desconto = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)
    itens = ItemInput(many=True)

    def validate_itens(self, value):
        if not value:
            raise serializers.ValidationError('O pedido deve ter pelo menos um item.')
        return value

    def create(self, validated_data):
        from produtos.models import Produto
        itens_data = validated_data.pop('itens')
        cliente_id = validated_data.pop('cliente_id')
        cliente = Cliente.objects.get(pk=cliente_id)

        pedido = Pedido.objects.create(cliente=cliente, **validated_data)
        for item in itens_data:
            produto = Produto.objects.get(pk=item['produto_id'])
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=item['quantidade'],
                preco_unitario=item.get('preco_unitario') or produto.preco,
            )
        pedido.save()  # recalcula totais
        return pedido


class AtualizarStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Pedido.Status.choices)
