from django.contrib import admin
from .models import Cliente, Pedido, ItemPedido, Carrinho, ItemCarrinho


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cidade', 'estado', 'ativo', 'data_cadastro')
    list_filter = ('ativo', 'estado')
    search_fields = ('nome', 'email', 'cpf')


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    readonly_fields = ('subtotal',)
    fields = ('produto', 'quantidade', 'preco_unitario', 'desconto_item', 'subtotal')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'cliente', 'status', 'forma_pagamento', 'total', 'data_pedido')
    list_filter = ('status', 'forma_pagamento')
    search_fields = ('numero', 'cliente__nome', 'cliente__email')
    readonly_fields = ('numero', 'subtotal', 'total', 'data_pedido', 'data_atualizacao')
    inlines = [ItemPedidoInline]


class ItemCarrinhoInline(admin.TabularInline):
    model = ItemCarrinho
    extra = 0
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        return obj.subtotal
    subtotal.short_description = 'Subtotal'


@admin.register(Carrinho)
class CarrinhoAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'sessao_id', 'quantidade_itens', 'total', 'atualizado_em')
    inlines = [ItemCarrinhoInline]

    def quantidade_itens(self, obj):
        return obj.quantidade_itens
    quantidade_itens.short_description = 'Qtd. Itens'

    def total(self, obj):
        return obj.total
    total.short_description = 'Total'
