# Bank API 

Esse é um exemplo de aplicação provendo uma API REST para a manipulação de um sistema
bancário simples, feita com Django/DRF.

## Manual de Execução

### Clone o repositório:
`git clone git@github.com:josevenzke/bank-api.git`

### Crie um ambiente virtual da sua forma preferida

### Instale os requirements:
`pip install -r requirements.txt`

### Entre no root do projeto:
`cd bank/`

### Faça as migrações da database:
`python manage.py makemigrations`
`python manage.py migrate`

### Inicie a aplicação:
`python manage.py runserver`

### Para executar os tests
`pytest -v`

## Documentação
`https://documenter.getpostman.com/view/15524648/UVJZoe8U`
Para executar as requests, abra a documentação no Desktop Agent
