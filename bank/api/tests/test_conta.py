import pytest
import json
from decimal import Decimal
from django.urls import reverse
from api.models import Pessoa,Conta
from datetime import datetime

contas_url = reverse("contas")
@pytest.mark.django_db
@pytest.fixture
def pessoa() -> Pessoa:
    return Pessoa.objects.create(nome="João", cpf="12345678910",dataNascimento='1999-10-10')

# ------------------ Test GET Contas ------------------------


@pytest.mark.django_db
def test_zero_contas_should_return_empty_list(client) -> None:
    response = client.get(contas_url)
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
def test_one_conta_exists(client,pessoa:Pessoa) -> None:
    test_conta = Conta.objects.create(saldo=0,limiteSaqueDiario=200.00,pessoa=pessoa)
    response = client.get(contas_url)
    response_content = json.loads(response.content)[0]

    assert response.status_code == 200
    assert Decimal(response_content.get("saldo")) == test_conta.saldo
    assert Decimal(response_content.get("limiteSaqueDiario")) == test_conta.limiteSaqueDiario
    assert response_content.get("flagAtivo") == test_conta.flagAtivo
    assert response_content.get("tipoConta") == test_conta.tipoConta
    assert response_content.get("pessoa") == test_conta.pessoa.id



@pytest.mark.django_db
def test_get_one_conta_by_id(client,pessoa:Pessoa) -> None:
    test_conta = Conta.objects.create(saldo=0,limiteSaqueDiario=200.00,pessoa=pessoa)
    conta_detail_url = reverse('conta-detail', kwargs={"id":pessoa.id})
    response = client.get(conta_detail_url)
    response_content = json.loads(response.content)
    assert response.status_code == 200
    assert Decimal(response_content.get("saldo")) == test_conta.saldo
    assert Decimal(response_content.get("limiteSaqueDiario")) == test_conta.limiteSaqueDiario
    assert response_content.get("flagAtivo") == test_conta.flagAtivo
    assert response_content.get("tipoConta") == test_conta.tipoConta
    assert response_content.get("pessoa") == test_conta.pessoa.id

# ------------------ Test POST Contas ------------------------

@pytest.mark.django_db
def test_create_conta_without_saldo(client,pessoa:Pessoa) -> None:
    response = client.post(contas_url, data={"limiteSaqueDiario":200.00,"pessoa":pessoa.id})
    assert response.status_code == 400
    assert json.loads(response.content) == {"saldo": ["Este campo é obrigatório."]}


@pytest.mark.django_db
def test_create_conta_without_limiteSaqueDiario(client,pessoa:Pessoa) -> None:
    response = client.post(contas_url, data={"saldo": 0,"pessoa":pessoa.id})
    assert response.status_code == 400
    assert json.loads(response.content) == {"limiteSaqueDiario": ["Este campo é obrigatório."]}


@pytest.mark.django_db
def test_create_conta_with_not_numeric_saldo(client,pessoa:Pessoa) -> None:
    response = client.post(contas_url, data={"saldo": "ads","limiteSaqueDiario":200.00,"pessoa":pessoa.id})
    assert response.status_code == 400
    assert json.loads(response.content) == {'saldo': ['Um número válido é necessário.']}


@pytest.mark.django_db
def test_create_conta(client,pessoa:Pessoa) -> None:
    response = client.post(contas_url, data={"saldo": 0,"limiteSaqueDiario":200.00,"pessoa":pessoa.id})
    response_content = json.loads(response.content)
    assert Decimal(response_content.get("saldo")) == 0
    assert Decimal(response_content.get("limiteSaqueDiario")) == 200.00
    assert response_content.get("flagAtivo") == True
    assert response_content.get("tipoConta") == 1
    assert response_content.get("pessoa") == 1
