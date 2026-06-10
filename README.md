# VoltStore — Catálogo de Produtos (AP2)

**Disciplina:** Big Data e Cloud Computing
**Avaliação:** AP2
**Autores:** Pedro Brito e João Pedro Bezamat

Continuação e expansão do projeto entregue na AP1 (Catálogo de Produtos API). Nesta etapa, a API foi ampliada para uma aplicação completa de comércio eletrônico (VoltStore), com interface web, novos módulos de domínio, banco de dados gerenciado, armazenamento de mídia em nuvem e painel administrativo.

---

## Tecnologias

* Python
* Django
* Django REST Framework
* PostgreSQL (Amazon RDS)
* Amazon S3 (django-storages, boto3)
* AWS Elastic Beanstalk
* gunicorn + Nginx
* WhiteNoise

---

## Deploy

A aplicação está disponível em:

http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/

---

## Links para avaliação

### Aplicação web (loja)
http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/

### API REST (Browsable API)
http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/api/

### Endpoints da API

| Recurso | URL |
|---------|-----|
| Produtos | http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/api/produtos/ |
| Fornecedores | http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/api/fornecedores/ |
| Clientes | http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/api/clientes/ |
| Carrinhos | http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/api/carrinhos/ |
| Pedidos | http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/api/pedidos/ |

### Painel administrativo (Django Admin)
http://voltstore-env.eba-y5hshcp9.us-east-1.elasticbeanstalk.com/admin/

| Campo | Valor |
|-------|-------|
| Usuário | `admin` |
| Senha | `123` |

---

## O que havia na AP1

A primeira entrega contemplava uma API REST simples com dois recursos:

* **Produto** e **Fornecedor**, com relação `ForeignKey`;
* `ProdutoViewSet` e `FornecedorViewSet` baseados em `ModelViewSet`;
* Roteamento via `DefaultRouter` em `/api/`;
* Banco SQLite;
* Deploy inicial no AWS Elastic Beanstalk com configuração padrão.

---

## O que foi adicionado na AP2

A AP2 transforma a API da AP1 em uma aplicação completa, com várias camadas adicionadas:

| Área | AP1 | AP2 |
|------|-----|-----|
| Domínio | Produto, Fornecedor | + Cliente, Carrinho, ItemCarrinho, Pedido, ItemPedido |
| Frontend | Apenas a Browsable API do DRF | Interface web (SPA em HTML + JS) servida pelo próprio Django |
| Upload de imagem | Não havia | Suporte a imagem por produto |
| Banco de dados | SQLite (arquivo local) | PostgreSQL gerenciado (Amazon RDS) |
| Armazenamento de mídia | Disco local | Amazon S3 |
| Administração | Apenas via API/Postman | Painel administrativo (Django Admin) |
| Permissões em nuvem | Não tratado | IAM Role com policies anexadas à instância EC2 |
| Estáticos em produção | Sem solução dedicada | WhiteNoise integrado |
| Provisionamento no deploy | Apenas o servidor | `migrate`, `collectstatic` e criação do superusuário automatizados |

---

## Endpoints (AP2)

### Produtos
* GET `/api/produtos/` — Lista produtos
* POST `/api/produtos/` — Cria produto (suporta upload de imagem em `multipart/form-data`)
* GET `/api/produtos/{id}/` — Detalhe
* PUT `/api/produtos/{id}/` — Atualiza
* DELETE `/api/produtos/{id}/` — Remove

### Fornecedores
* GET `/api/fornecedores/` — Lista fornecedores
* POST `/api/fornecedores/` — Cria fornecedor

### Clientes
* GET `/api/clientes/` — Lista clientes
* POST `/api/clientes/` — Cria cliente

### Carrinhos
* GET `/api/carrinhos/` — Lista carrinhos (suporta `?abertos=true`)
* POST `/api/carrinhos/` — Cria carrinho para um cliente
* POST `/api/carrinhos/{id}/adicionar/` — Adiciona item ao carrinho
* POST `/api/carrinhos/{id}/checkout/` — Fecha o carrinho e gera o pedido

### Pedidos
* GET `/api/pedidos/` — Lista pedidos (suporta `?status=PENDENTE`)
* GET `/api/pedidos/{id}/` — Detalhe do pedido
* PATCH `/api/pedidos/{id}/` — Atualiza status

---

## Exemplos de requisição

### Criar fornecedor
```json
POST /api/fornecedores/
{
  "nome": "Fornecedor Teste",
  "email": "teste@email.com",
  "telefone": "123456789"
}
```

### Criar produto
```json
POST /api/produtos/
{
  "nome": "Notebook",
  "descricao": "Notebook gamer",
  "preco": 3500.00,
  "fornecedor": 1
}
```

### Criar cliente
```json
POST /api/clientes/
{
  "nome": "Maria da Silva",
  "email": "maria@email.com",
  "cpf": "12345678901"
}
```

### Adicionar item ao carrinho
```json
POST /api/carrinhos/1/adicionar/
{
  "produto": 1,
  "quantidade": 2
}
```

---

## Execução local

```
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Sem variáveis de ambiente configuradas, o projeto usa SQLite e armazenamento de mídia em disco automaticamente — útil para desenvolvimento.

---

## Desenvolvimento

### Classe Fornecedor *(mantida da AP1)*

A entidade **Fornecedor** representa os responsáveis pelos produtos do sistema. Mantém os campos definidos na AP1:

* `nome`: identificação do fornecedor
* `email`: contato principal
* `telefone`: contato adicional
* `ativo`: controle de status (ativo/inativo)

---

### Relacionamento com Produto *(mantido da AP1)*

A classe **Produto** possui chave estrangeira para Fornecedor:

* Tipo: `ForeignKey`
* Regra de exclusão: `SET_NULL`
* Relação reversa: `produtos`

Na AP2, a entidade foi acrescida do campo `imagem` (`ImageField`), com upload direto pelo formulário do front e armazenamento no Amazon S3.

---

### Novas classes de domínio *(adicionadas na AP2)*

Para suportar o fluxo completo de comércio eletrônico, foram criadas as seguintes entidades no app `pedidos`:

* **Cliente** — dados do consumidor (nome, e-mail, CPF, telefone, endereço);
* **Carrinho** — vinculado a um cliente, agrega itens antes do fechamento;
* **ItemCarrinho** — relação entre carrinho e produto, com quantidade;
* **Pedido** — gerado a partir do carrinho no checkout; possui número (gerado automaticamente no formato `PED-000001`), status, forma de pagamento e total;
* **ItemPedido** — congelamento dos itens do carrinho no momento do checkout.

As relações foram definidas com `ForeignKey` e regras de exclusão apropriadas, e os totais são recalculados automaticamente ao alterar itens.

---

### Construção da API *(expandida)*

Mantendo a abordagem adotada na AP1 (`ModelViewSet` com `DefaultRouter`), foram acrescentados os ViewSets:

* `ClienteViewSet`
* `CarrinhoViewSet` (com ações customizadas `adicionar` e `checkout`)
* `PedidoViewSet` (com filtro por status)

---

### Roteamento *(expandido)*

O roteador central (`catalogo/api.py`) registra todos os recursos:

```python
router.register(r'produtos', ProdutoViewSet)
router.register(r'fornecedores', FornecedorViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'carrinhos', CarrinhoViewSet)
router.register(r'pedidos', PedidoViewSet)
```

Resultando nos endpoints listados na seção anterior, todos sob o prefixo `/api/`.

---

### Interface web (front-end) *(novo na AP2)*

Foi construída uma aplicação `loja` que serve uma página única (HTML + JavaScript puro, sem framework ou build) com tema escuro. A página consome a própria API REST e implementa as abas:

* Loja (catálogo, cadastro/edição de produtos com upload de imagem)
* Fornecedores
* Clientes
* Carrinho
* Pedidos

---

### Migração do banco de dados *(novo na AP2)*

Na AP1, o banco utilizado em produção era o SQLite. Na AP2, foi adotado o **Amazon RDS (PostgreSQL 16)**:

* Instância `db.t3.micro`, nome `voltstore-db`, região `us-east-1`;
* Conexão configurada por variáveis de ambiente (`DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`, `DB_SSLMODE`);
* SSL exigido (`sslmode=require`).

O `settings.py` mantém compatibilidade com SQLite quando `DB_HOST` não está definido, facilitando o desenvolvimento local.

---

### Armazenamento de mídia no S3 *(novo na AP2)*

Para que as imagens dos produtos sobrevivam a reinicializações do servidor (instâncias EC2 do Beanstalk são efêmeras), o armazenamento foi movido para o **Amazon S3**:

* Bucket `voltstore-midia-jpbrito2026` (região `us-east-1`);
* Integração via `django-storages` e `boto3`;
* Credenciais obtidas automaticamente da IAM Role da instância;
* Bucket Policy permitindo leitura pública apenas no prefixo `media/`;
* CORS configurado para leitura pelo navegador.

---

### Painel administrativo *(novo na AP2)*

O Django Admin foi habilitado em `/admin/`. Para criar o superusuário sem necessidade de acesso SSH, foi implementado um *management command* customizado (`criar_superuser`) que lê as credenciais de variáveis de ambiente e cria o usuário durante o deploy.

---

### Estáticos com WhiteNoise *(novo na AP2)*

Como o Django Admin depende de arquivos CSS/JS estáticos, foi integrado o **WhiteNoise**, que serve esses arquivos diretamente pela aplicação, sem dependência adicional do nginx.

---

### Testes

A validação das requisições foi feita com **Postman** (mantendo a metodologia da AP1) e por uso direto da aplicação web em produção:

* Criação e edição de fornecedores, clientes, produtos e pedidos;
* Upload de imagens de produtos (verificação da gravação no bucket S3);
* Fluxo completo de compra: adicionar ao carrinho → checkout → consulta no painel administrativo;
* Verificação das respostas em formato JSON via Browsable API.

---

### Deploy

O deploy continua sendo feito no **AWS Elastic Beanstalk**, agora com os seguintes incrementos em relação à AP1:

* Configuração de variáveis de ambiente sensíveis (segredos do Django e do banco) diretamente nas *Environment Properties*;
* Arquivo `.ebextensions/django.config` que executa, em cada deploy:
  * `python manage.py migrate --noinput`
  * `python manage.py collectstatic --noinput`
  * `python manage.py criar_superuser`
* Anexação de policies (`AmazonS3FullAccess`, `AmazonSSMManagedInstanceCore`) à IAM Role da instância (`aws-elasticbeanstalk-ec2-role`), permitindo o acesso ao S3 e o uso do Session Manager.

---

## Desafios enfrentados

Durante a implantação na AWS, surgiram dificuldades técnicas que exigiram ajustes sucessivos. Os principais grupos estão descritos abaixo.

### Conectividade entre Elastic Beanstalk e RDS

Mesmo com EB e RDS provisionados na mesma VPC, a conexão inicial falhava por causa de regras de Security Group. A solução foi ajustar as regras de entrada do banco para aceitar tráfego do próprio Security Group da instância da aplicação.

### Configuração de permissões IAM

A conta utilizada (AWS Academy / estudante) possui *Service Control Policies* que impedem a criação de usuários IAM convencionais. Adotou-se a abordagem recomendada pela AWS: anexar políticas diretamente à **IAM Role** da instância EC2, permitindo que o `boto3` utilize essas credenciais de forma transparente.

### Diagnóstico de erros em produção

Inicialmente, falhas no upload de imagens retornavam HTTP 500 sem informação de causa. Foi necessário configurar explicitamente o `LOGGING` do Django para que os traces de exceção fossem exibidos nos logs do Beanstalk, viabilizando o diagnóstico das causas reais (permissões IAM ausentes, métodos do S3 e detalhes da biblioteca `django-storages`).

### Servidor de arquivos estáticos e Django Admin

A configuração padrão do WhiteNoise utilizava um backend que exige um *manifest* completo dos arquivos estáticos, gerando erro 500 no admin. Adicionalmente, havia conflito entre o WhiteNoise e o mapeamento de estáticos do nginx do Beanstalk. A solução foi adotar um backend mais tolerante e remover o mapeamento conflitante.

### Cookies e CSRF em conexão sem TLS

Como a aplicação está publicada em HTTP, as flags padrão de segurança do Django (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`) impediam o login no admin, e a validação de CSRF rejeitava os formulários por origem não confiável. As configurações foram tornadas controláveis por variável de ambiente, e `CSRF_TRUSTED_ORIGINS` passou a incluir tanto `http://` quanto `https://`.

---

## Observações

* Por se tratar de um projeto acadêmico, optou-se por HTTP (sem certificado TLS), instâncias de baixo custo e regras de rede permissivas. Em produção real, esses pontos deveriam ser revisados.
* O upload de imagens grandes pode exigir ajuste de `client_max_body_size` no nginx do Beanstalk.
* O banco padrão em desenvolvimento local continua sendo SQLite (não recomendado para produção, mas conveniente para testes locais).

---

## Licença

Projeto acadêmico — entrega da AP2 da disciplina de Big Data e Cloud Computing.
