from rest_framework.decorators import api_view
from rest_framework.response import Response
import decimal
import datetime
from .models import Pessoa, Conta, Transacao
from .serializers import PessoaSerializer, ContaSerializer, TransacaoSerializer
from .functions import is_decimal
from django.shortcuts import get_object_or_404

# Create your views here.


from rest_framework.decorators import api_view


@api_view(["GET", "POST"])
def pessoas(request):
    if request.method == "POST":
        serializer_pessoa = PessoaSerializer(data=request.data)
        if serializer_pessoa.is_valid():
            serializer_pessoa.save()
            return Response({"pessoa": serializer_pessoa.data})

        else:
            return Response([serializer_pessoa.errors], status=400)

    pessoas = Pessoa.objects.all()
    pessoas_serialized = PessoaSerializer(pessoas, many=True)
    return Response(pessoas_serialized.data)


@api_view(["GET"])
def pessoas_detail(request, id):
    pessoa = get_object_or_404(Pessoa, pk=id)
    pessoa_serialized = PessoaSerializer(pessoa)
    return Response(pessoa_serialized.data)


@api_view(["GET", "POST"])
def contas(request):
    if request.method == "POST":
        serializer_conta = ContaSerializer(data=request.data)
        if serializer_conta.is_valid():
            serializer_conta.save()
            return Response({"conta": serializer_conta.data})

        else:
            return Response([serializer_conta.errors], status=400)

    contas = Conta.objects.all()
    contas_serialized = ContaSerializer(contas, many=True)
    return Response(contas_serialized.data)


@api_view(["GET"])
def contas_detail(request, id):
    conta = get_object_or_404(Conta, pk=id)
    conta_serialized = ContaSerializer(conta)
    return Response(conta_serialized.data)


@api_view(["POST"])
def deposito(request, id):
    valor = request.POST.get("valor")
    if not is_decimal(valor):
        return Response({"valor": "Make sure valor exists and is numeric"})

    conta = get_object_or_404(Conta, pk=id)
    valor = decimal.Decimal(valor)
    conta.saldo += valor
    transacao = Transacao(conta=conta, valor=valor)
    conta.save()
    transacao.save()
    conta_serialized = ContaSerializer(conta)
    transacao_serialized = TransacaoSerializer(transacao)
    return Response(
        {"conta": conta_serialized.data, "transacao": transacao_serialized.data}
    )


@api_view(["POST"])
def saque(request, id):
    valor = request.POST.get("valor")
    if not is_decimal(valor):
        return Response({"valor": "Make sure valor exists and is numeric"})

    conta = get_object_or_404(Conta, pk=id)
    if float(valor) > conta.saldo:
        return Response({"valor": "You do not have enough saldo"})

    valor = decimal.Decimal(valor)
    conta.saldo -= valor
    transacao = Transacao(conta=conta, valor=valor)
    conta.save()
    transacao.save()
    conta_serialized = ContaSerializer(conta)
    transacao_serialized = TransacaoSerializer(transacao)
    return Response(
        {"conta": conta_serialized.data, "transacao": transacao_serialized.data}
    )


@api_view(["POST"])
def bloqueio(request, id):
    conta = get_object_or_404(Conta, pk=id)
    conta.flagAtivo = False
    conta.save()
    conta_serialized = ContaSerializer(conta)
    return Response({"conta": conta_serialized.data})


@api_view(["POST"])
def desbloqueio(request, id):
    conta = get_object_or_404(Conta, pk=id)
    conta.flagAtivo = True
    conta.save()
    conta_serialized = ContaSerializer(conta)
    return Response({"conta": conta_serialized.data})


@api_view(["GET"])
def saldo(request, id):
    conta = get_object_or_404(Conta, pk=id)
    saldo = conta.saldo
    return Response({"saldo": saldo})


@api_view(["GET"])
def transacoes(request, id):
    data_inicial = request.POST.get("data_inicial")
    data_final = request.POST.get("data_final")
    if data_inicial:
        if not data_final:
            data_final = datetime.datetime.now()
        try:
            transacao = Transacao.objects.filter(
                dataTransacao__gte=data_inicial, dataTransacao__lte=data_final
            )
        except Exception as e:
            return Response({"data": e})
        serializer = TransacaoSerializer(transacao, many=True)
        return Response(serializer.data)

    transacao = Transacao.objects.filter(conta=id)
    serializer = TransacaoSerializer(transacao, many=True)
    return Response(serializer.data)
