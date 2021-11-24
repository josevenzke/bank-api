import pytest
import json
from decimal import Decimal

from django.urls import reverse

from api.models import Pessoa, Conta


contas_url = reverse("contas")

# ------------------ Test GET Contas ------------------------


@pytest.mark.django_db
def test_zero_contas_deve_reornar_lista_vazia(client) -> None:
    response = client.get(contas_url)
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
@pytest.fixture
def pessoa() -> Pessoa:
    return Pessoa.objects.create(
        nome="João", cpf="12345678910", dataNascimento="1999-10-10"
    )


@pytest.mark.django_db
def test_uma_conta_existe(client, pessoa: Pessoa) -> None:
    test_conta = Conta.objects.create(saldo=0, limiteSaqueDiario=200.00, pessoa=pessoa)
    response = client.get(contas_url)
    response_content = json.loads(response.content)[0]

    assert response.status_code == 200
    assert Decimal(response_content.get("saldo")) == test_conta.saldo
    assert (
        Decimal(response_content.get("limiteSaqueDiario"))
        == test_conta.limiteSaqueDiario
    )
    assert response_content.get("flagAtivo") == test_conta.flagAtivo
    assert response_content.get("tipoConta") == test_conta.tipoConta
    assert response_content.get("pessoa") == test_conta.pessoa.id


@pytest.mark.django_db
def test_get_uma_conta_por_id(client, pessoa: Pessoa) -> None:
    test_conta = Conta.objects.create(saldo=0, limiteSaqueDiario=200.00, pessoa=pessoa)
    conta_detail_url = reverse("conta-detail", kwargs={"id": pessoa.id})
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
def test_cirar_conta_sem_saldo(client, pessoa: Pessoa) -> None:
    response = client.post(
        contas_url, data={"limiteSaqueDiario": 200.00, "pessoa": pessoa.id}
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {"saldo": ["Este campo é obrigatório."]}


@pytest.mark.django_db
def test_cirar_conta_sem_limiteSaqueDiario(client, pessoa: Pessoa) -> None:
    response = client.post(contas_url, data={"saldo": 0, "pessoa": pessoa.id})
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "limiteSaqueDiario": ["Este campo é obrigatório."]
    }


@pytest.mark.django_db
def test_criar_conta_com_saldo_nao_numerico(client, pessoa: Pessoa) -> None:
    response = client.post(
        contas_url,
        data={"saldo": "ads", "limiteSaqueDiario": 200.00, "pessoa": pessoa.id},
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {"saldo": ["Um número válido é necessário."]}


@pytest.mark.django_db
def test_criar_conta(client, pessoa: Pessoa) -> None:
    response = client.post(
        contas_url, data={"saldo": 0, "limiteSaqueDiario": 200.00, "pessoa": pessoa.id}
    )
    response_content = json.loads(response.content)
    assert Decimal(response_content.get("saldo")) == 0
    assert Decimal(response_content.get("limiteSaqueDiario")) == 200.00
    assert response_content.get("flagAtivo") == True
    assert response_content.get("tipoConta") == 1
    assert response_content.get("pessoa") == 1


# ------------------ Test Deposito/Saque ------------------------


@pytest.mark.django_db
@pytest.fixture
def conta(pessoa: Pessoa) -> Conta:
    return Conta.objects.create(saldo=100, limiteSaqueDiario=50.00, pessoa=pessoa)


@pytest.mark.django_db
def test_deposito_sem_valor(client, conta: Conta) -> None:
    response = client.post(reverse("deposito", kwargs={"id": conta.id}), data={})
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "valor": "Valor tem que existir e ser numérico"
    }


@pytest.mark.django_db
def test_deposito_valor_nao_numerico(client, conta: Conta) -> None:
    response = client.post(
        reverse("deposito", kwargs={"id": conta.id}), data={"valor": "1asd23"}
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "valor": "Valor tem que existir e ser numérico"
    }


@pytest.mark.django_db
def test_deposito(client, conta: Conta) -> None:
    saldo_antigo = conta.saldo
    response = client.post(
        reverse("deposito", kwargs={"id": conta.id}), data={"valor": "10.5"}
    )
    response_content = json.loads(response.content)
    assert response.status_code == 200
    assert Decimal(response_content["conta"].get("saldo")) == Decimal(saldo_antigo + 10.5)
    assert Decimal(response_content["transacao"].get("valor")) == Decimal(10.5)


@pytest.mark.django_db
def test_saque_sem_valor(client, conta: Conta) -> None:
    response = client.post(reverse("saque", kwargs={"id": conta.id}), data={})
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "valor": "Valor tem que existir e ser numérico"
    }


@pytest.mark.django_db
def test_saque_valor_maior_que_saldo(client, conta: Conta) -> None:
    response = client.post(
        reverse("saque", kwargs={"id": conta.id}), data={"valor": 201}
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {"valor": "A conta não tem saldo suficiente"}


@pytest.mark.django_db
def test_saque_valor_excede_limite_diario(client, conta: Conta) -> None:
    response = client.post(
        reverse("saque", kwargs={"id": conta.id}), data={"valor": 20}
    )
    response = client.post(
        reverse("saque", kwargs={"id": conta.id}), data={"valor": 20}
    )
    response = client.post(
        reverse("saque", kwargs={"id": conta.id}), data={"valor": 20}
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "limiteSaqueDiario": "Essa operação excedera o limite de saque diário desta conta"
    }


@pytest.mark.django_db
def test_saque(client, conta: Conta) -> None:
    saldo_antigo = conta.saldo
    response = client.post(
        reverse("saque", kwargs={"id": conta.id}), data={"valor": "10.5"}
    )
    response_content = json.loads(response.content)
    assert response.status_code == 200
    assert Decimal(response_content["conta"].get("saldo")) == Decimal(saldo_antigo - 10.5)
    assert Decimal(response_content["transacao"].get("valor")) == Decimal(10.5)


# ------------------ Test Bloqueio/Desbloqueio ------------------------


@pytest.mark.django_db
def test_bloqueio(client, conta: Conta) -> None:
    response = client.post(reverse("bloqueio", kwargs={"id": conta.id}))
    response_content = json.loads(response.content)
    assert response.status_code == 200
    assert response_content.get("flagAtivo") == False


@pytest.mark.django_db
def test_desbloqueio(client, conta: Conta) -> None:
    response = client.post(reverse("desbloqueio", kwargs={"id": conta.id}))
    response_content = json.loads(response.content)
    assert response.status_code == 200
    assert response_content.get("flagAtivo") == True
