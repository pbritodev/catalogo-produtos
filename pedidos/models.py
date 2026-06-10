from django.db import models
from django.contrib.auth.models import User
from produtos.models import Produto


class Cliente(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cliente'
    )
    nome = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=14, unique=True)
    endereco = models.CharField(max_length=300, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)
    cep = models.CharField(max_length=9, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'pendente', 'Pendente'
        CONFIRMADO = 'confirmado', 'Confirmado'
        EM_PREPARO = 'em_preparo', 'Em Preparo'
        ENVIADO = 'enviado', 'Enviado'
        ENTREGUE = 'entregue', 'Entregue'
        CANCELADO = 'cancelado', 'Cancelado'

    class FormaPagamento(models.TextChoices):
        CARTAO_CREDITO = 'cartao_credito', 'Cartão de Crédito'
        CARTAO_DEBITO = 'cartao_debito', 'Cartão de Débito'
        PIX = 'pix', 'PIX'
        BOLETO = 'boleto', 'Boleto'
        DINHEIRO = 'dinheiro', 'Dinheiro'

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name='pedidos'
    )
    numero = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDENTE
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FormaPagamento.choices,
        blank=True
    )
    endereco_entrega = models.CharField(max_length=300, blank=True)
    observacoes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    frete = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_pedido']

    def __str__(self):
        return f'Pedido {self.numero} — {self.cliente.nome}'

    def save(self, *args, **kwargs):
        # Gera número sequencial na primeira vez
        if not self.pk:
            super().save(*args, **kwargs)
            self.numero = f'PED-{self.pk:06d}'
            kwargs['force_insert'] = False
        self.recalcular_totais()
        super().save(*args, **kwargs)

    def recalcular_totais(self):
        self.subtotal = sum(
            item.subtotal for item in self.itens.all()
        )
        self.total = self.subtotal - self.desconto + self.frete


class ItemPedido(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        related_name='itens_pedido'
    )
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    desconto_item = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome} (Pedido {self.pedido.numero})'

    def save(self, *args, **kwargs):
        # Captura preço vigente do produto se não informado
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        self.subtotal = (self.preco_unitario * self.quantidade) - self.desconto_item
        super().save(*args, **kwargs)
        # Recalcula totais do pedido
        self.pedido.save()


class Carrinho(models.Model):
    """Carrinho de compras temporário antes de virar Pedido."""
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        related_name='carrinho',
        null=True,
        blank=True
    )
    sessao_id = models.CharField(max_length=100, blank=True, db_index=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        owner = self.cliente.nome if self.cliente else f'Sessão {self.sessao_id}'
        return f'Carrinho de {owner}'

    @property
    def total(self):
        return sum(item.subtotal for item in self.itens.all())

    @property
    def quantidade_itens(self):
        return sum(item.quantidade for item in self.itens.all())

    def converter_em_pedido(self, forma_pagamento='', observacoes=''):
        """Converte o carrinho em um Pedido e limpa os itens."""
        if not self.cliente:
            raise ValueError('Carrinho sem cliente não pode ser convertido em pedido.')
        if not self.itens.exists():
            raise ValueError('Carrinho vazio.')

        pedido = Pedido.objects.create(
            cliente=self.cliente,
            forma_pagamento=forma_pagamento,
            observacoes=observacoes,
            endereco_entrega=self.cliente.endereco,
        )
        for item_carrinho in self.itens.all():
            ItemPedido.objects.create(
                pedido=pedido,
                produto=item_carrinho.produto,
                quantidade=item_carrinho.quantidade,
                preco_unitario=item_carrinho.produto.preco,
            )
        self.itens.all().delete()
        return pedido


class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(
        Carrinho,
        on_delete=models.CASCADE,
        related_name='itens'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='itens_carrinho'
    )
    quantidade = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ('carrinho', 'produto')

    def __str__(self):
        return f'{self.quantidade}x {self.produto.nome}'

    @property
    def subtotal(self):
        return self.produto.preco * self.quantidade
