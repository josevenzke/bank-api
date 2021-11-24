import decimal
import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Pessoa, Conta, Transacao
from .serializers import PessoaSerializer, ContaSerializer, TransacaoSerializer
from .functions import is_decimal

from rest_framework.decorators import api_view


@api_view(["GET", "POST"])
def pessoas(request):
    """GET: retorna uma lista com todas as pessoas registradas
       POST: recebe um nome,cpf e dataNascimento, cria uma nova pessoa
       e retorna esse objeto"""
    if request.method == "POST":
        serializer_pessoa = PessoaSerializer(data=request.data)
        if serializer_pessoa.is_valid():
            serializer_pessoa.save()
            return Response(serializer_pessoa.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer_pessoa.errors, status=status.HTTP_400_BAD_REQUEST)

    pessoas = Pessoa.objects.all()
    pessoas_serialized = PessoaSerializer(pessoas, many=True)
    return Response(pessoas_serialized.data)


@api_view(["GET"])
def pessoas_detail(request, id):
    """Recebe um parametro id e retorna um objeto Pessoa especifico"""
    pessoa = get_object_or_404(Pessoa, pk=id)
    pessoa_serialized = PessoaSerializer(pessoa)
    return Response(pessoa_serialized.data)


@api_view(["GET", "POST"])
def contas(request):
    """GET: retorna uma lista com todas as contas criadas
       POST: recebe obrigatoriamente um saldo,limiteSaqueDiario e uma pessoa_id, cria uma nova conta
       e retorna esse objeto"""
    if request.method == "POST":
        serializer_conta = ContaSerializer(data=request.data)
        if serializer_conta.is_valid():
            serializer_conta.save()
            return Response(serializer_conta.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer_conta.errors, status=status.HTTP_400_BAD_REQUEST)

    contas = Conta.objects.all()
    contas_serialized = ContaSerializer(contas, many=True)
    return Response(contas_serialized.data)


@api_view(["GET"])
def contas_detail(request, id):
    """Recebe um parametro id e retorna um objeto Conta especifico"""
    conta = get_object_or_404(Conta, pk=id)
    conta_serialized = ContaSerializer(conta)
    return Response(conta_serialized.data)


@api_view(["POST"])
def deposito(request, id):
    """Recebe um parametro id e um valor e faz um deposito
       na conta especificada"""
    valor = request.POST.get("valor")
    if not is_decimal(valor):
        return Response(
            {"valor": "Make sure valor exists and is numeric"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    conta = get_object_or_404(Conta, pk=id)
    valor = decimal.Decimal(valor)
    conta.saldo += valor
    transacao = Transacao(conta=conta, valor=valor,tipo="deposito")
    conta.save()
    transacao.save()
    conta_serialized = ContaSerializer(conta)
    transacao_serialized = TransacaoSerializer(transacao)
    return Response(
        {"conta": conta_serialized.data, "transacao": transacao_serialized.data}
    )


@api_view(["POST"])
def saque(request, id):
    """Recebe um parametro id e um valor e faz um saque
       na conta especificada, caso o limiteSaqueDiario não
       seja excedido e haja saldo o suficiente"""
    valor = request.POST.get("valor")
    if not is_decimal(valor):
        return Response(
            {"valor": "Make sure valor exists and is numeric"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    conta = get_object_or_404(Conta, pk=id)
    if float(valor) > conta.saldo:
        return Response(
            {"valor": "You do not have enough saldo"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    transacoes = Transacao.objects.filter(
        conta_id=id, dataTransacao__date=datetime.datetime.today().strftime("%Y-%m-%d"),tipo="saque"
    ).values_list()
    gasto_diario = 0
    for transacao in transacoes:
        gasto_diario += transacao[1]

    valor = decimal.Decimal(valor)

    if (gasto_diario + valor) > conta.limiteSaqueDiario:
        return Response(
            {
                "limiteSaqueDiario": "Essa operação excedera o limite de saque diário desta conta"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    conta.saldo -= valor
    transacao = Transacao(conta=conta, valor=valor,tipo="saque")
    conta.save()
    transacao.save()
    conta_serialized = ContaSerializer(conta)
    transacao_serialized = TransacaoSerializer(transacao)
    return Response(
        {"conta": conta_serialized.data, "transacao": transacao_serialized.data}
    )


@api_view(["POST"])
def bloqueio(request, id):
    """Recebe um parametro id e bloqueia uma conta especifica"""
    conta = get_object_or_404(Conta, pk=id)
    conta.flagAtivo = False
    conta.save()
    conta_serialized = ContaSerializer(conta)
    return Response(conta_serialized.data)


@api_view(["POST"])
def desbloqueio(request, id):
    """Recebe um parametro id e desbloqueia uma conta especifica"""
    conta = get_object_or_404(Conta, pk=id)
    conta.flagAtivo = True
    conta.save()
    conta_serialized = ContaSerializer(conta)
    return Response(conta_serialized.data)


@api_view(["GET"])
def saldo(request, id):
    """Recebe um parametro id e retorna o saldo de uma conta especifica"""
    conta = get_object_or_404(Conta, pk=id)
    saldo = conta.saldo
    return Response({"saldo": saldo})


@api_view(["GET"])
def transacoes(request, id):
    """Recebe um parametro id, e opcionalmente uma data inicial/final e 
    retorna as transações no periodo ou no geral da conta especificada"""
    data_inicial = request.POST.get("data_inicial")
    data_final = request.POST.get("data_final")
    if data_inicial:
        if not data_final:
            data_final = datetime.datetime.now()
        try:
            transacao = Transacao.objects.filter(
                conta_id=id,
                dataTransacao__range=[data_inicial, data_final]
            )
        except Exception as e:
            return Response({"data": e}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TransacaoSerializer(transacao, many=True)
        return Response(serializer.data)

    transacao = Transacao.objects.filter(conta=id)
    serializer = TransacaoSerializer(transacao, many=True)
    return Response(serializer.data)
