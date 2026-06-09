### link da api: http://catalogo-produtos-env.eba-upcvmi9k.us-east-1.elasticbeanstalk.com/
### link da aba produtos: http://catalogo-produtos-env.eba-upcvmi9k.us-east-1.elasticbeanstalk.com/api/produtos
### link da aba fornecedores: http://catalogo-produtos-env.eba-upcvmi9k.us-east-1.elasticbeanstalk.com/api/fornecedores

# Catálogo de Produtos API

API REST para gerenciamento de produtos e fornecedores, desenvolvida com Django e Django REST Framework e publicada na AWS Elastic Beanstalk.

---

## Tecnologias

* Python
* Django
* Django REST Framework
* AWS Elastic Beanstalk
* Nginx

---

## Deploy

A API está disponível em:


http://catalogo-produtos-env.eba-upcvmi9k.us-east-1.elasticbeanstalk.com/


---

## Endpoints

### Produtos

* GET /api/produtos/ — Lista produtos
* POST /api/produtos/ — Cria produto
* GET /api/produtos/{id}/ — Detalhe
* PUT /api/produtos/{id}/ — Atualiza
* DELETE /api/produtos/{id}/ — Remove

---

### Fornecedores

* GET /api/fornecedores/ — Lista fornecedores
* POST /api/fornecedores/ — Cria fornecedor

---

## Exemplos de requisição

### Criar fornecedor

json
POST /api/fornecedores/

{
  "nome": "Fornecedor Teste",
  "email": "teste@email.com",
  "telefone": "123456789"
}


---

### Criar produto

json
POST /api/produtos/

{
  "nome": "Notebook",
  "descricao": "Notebook gamer",
  "preco": 3500.00,
  "fornecedor": 1
}


---

## Admin Django

Acesse o painel administrativo:


/admin


---

## Execução local

pip install -r requirements.txt
---
python manage.py migrate
---
python manage.py runserver
---


---

## Deploy

Deploy realizado utilizando AWS Elastic Beanstalk com configuração padrão para aplicações Python.

---

## Observações

* Upload de imagens requer ajuste no Nginx (client_max_body_size)
* API utiliza relacionamento entre Produto e Fornecedor
* Banco padrão pode ser SQLite (não recomendado para produção)

---

## Licença

Projeto acadêmico.

## Desenvolvimento

### Classe Fornecedor

A entidade *Fornecedor* foi criada para representar os responsáveis pelos produtos cadastrados no sistema.
Foram definidos os seguintes campos:

* nome: identificação do fornecedor
* email: contato principal
* telefone: contato adicional
* ativo: controle de status (ativo/inativo)

A modelagem utilizou o ORM do Django, permitindo integração direta com o banco de dados e operações CRUD automáticas.

---

### Relacionamento com Produto

A classe *Produto* possui uma relação de chave estrangeira com Fornecedor:

* Tipo: ForeignKey
* Regra de exclusão: SET_NULL
* Relação reversa: produtos

Isso permite associar múltiplos produtos a um único fornecedor, mantendo a integridade dos dados.

---

### Construção da API

A API foi implementada utilizando *Django REST Framework*, adotando ModelViewSet para reduzir código e acelerar o desenvolvimento.

Foram criados dois ViewSets:

* ProdutoViewSet
* FornecedorViewSet

Esses componentes fornecem automaticamente operações:

* Listagem (GET)
* Criação (POST)
* Atualização (PUT)
* Remoção (DELETE)

---

### Roteamento

O roteamento foi configurado com DefaultRouter, que gera automaticamente os endpoints da API:

python
router.register(r'produtos', ProdutoViewSet)
router.register(r'fornecedores', FornecedorViewSet)


As rotas foram expostas com prefixo /api/, resultando em endpoints como:

* /api/produtos/
* /api/fornecedores/

---

### Testes

Os testes da API foram realizados utilizando o Postman, validando:

* Criação de fornecedores
* Criação de produtos vinculados
* Listagem de dados
* Respostas em formato JSON

---

### Deploy

Após validação local, a aplicação foi publicada na AWS Elastic Beanstalk, mantendo a mesma estrutura da API e garantindo acesso remoto aos endpoints.
