import pytest
import json

from django.urls import reverse
from api.models import Pessoa


pessoas_url = reverse("pessoas")

# ------------------ Test GET Pessoas ------------------------


@pytest.mark.django_db
def test_zero_pessoas_deve_retornar_lista_vazia(client) -> None:
    response = client.get(pessoas_url)
    assert response.status_code == 200
    assert json.loads(response.content) == []


@pytest.mark.django_db
def test_uma_pessoa_existe(client) -> None:
    test_pessoa = Pessoa.objects.create(
        nome="João", cpf="12345678910", dataNascimento="1999-10-10"
    )
    response = client.get(pessoas_url)
    response_content = json.loads(response.content)[0]
    assert response.status_code == 200
    assert response_content.get("nome") == test_pessoa.nome
    assert response_content.get("cpf") == test_pessoa.cpf
    assert response_content.get("dataNascimento") == test_pessoa.dataNascimento


@pytest.mark.django_db
def test_get_uma_pessoa_por_id(client) -> None:
    test_pessoa = Pessoa.objects.create(
        nome="João", cpf="12345678910", dataNascimento="1999-10-10"
    )
    pessoa_detail_url = reverse("pessoa-detail", kwargs={"id": test_pessoa.id})
    response = client.get(pessoa_detail_url)
    response_content = json.loads(response.content)
    assert response.status_code == 200
    assert response_content.get("nome") == test_pessoa.nome
    assert response_content.get("cpf") == test_pessoa.cpf
    assert response_content.get("dataNascimento") == test_pessoa.dataNascimento


# ------------------ Test POST Pessoas ------------------------


@pytest.mark.django_db
def test_criar_pessoa_sem_nome(client) -> None:
    response = client.post(
        pessoas_url, data={"cpf": "12345678910", "dataNascimento": "1999-10-10"}
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {"nome": ["Este campo é obrigatório."]}


@pytest.mark.django_db
def test_criar_pessoa_sem_cpf(client) -> None:
    response = client.post(
        pessoas_url, data={"nome": "João", "dataNascimento": "1999-10-10"}
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {"cpf": ["Este campo é obrigatório."]}


@pytest.mark.django_db
def test_criar_pessoa_sem_dataNascimento(client) -> None:
    response = client.post(pessoas_url, data={"nome": "João", "cpf": "12345678910"})
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "dataNascimento": ["Este campo é obrigatório."]
    }


@pytest.mark.django_db
def test_criar_pessoa_com_tamanho_errado_cpf(client) -> None:
    response = client.post(
        pessoas_url,
        data={"nome": "João", "cpf": "1234567891", "dataNascimento": "1999-10-10"},
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "cpf": ["CPF deve conter 11 e não 10 dígitos"]
    }


@pytest.mark.django_db
def test_criar_pessoa_com_cpf_nao_numerico(client) -> None:
    response = client.post(
        pessoas_url,
        data={"nome": "João", "cpf": "12345678asd", "dataNascimento": "1999-10-10"},
    )
    assert response.status_code == 400
    assert json.loads(response.content) == {"cpf": ["CPF deve conter apenas números"]}


@pytest.mark.django_db
def test_criar_pessoa(client) -> None:
    response = client.post(
        pessoas_url,
        data={"nome": "João", "cpf": "12345678910", "dataNascimento": "1999-10-10"},
    )
    response_content = json.loads(response.content)
    assert response.status_code == 201
    assert response_content.get("nome") == "João"
    assert response_content.get("cpf") == "12345678910"
    assert response_content.get("dataNascimento") == "1999-10-10"
