from rest_framework import serializers
from django.core.exceptions import ValidationError

from .models import Pessoa, Conta, Transacao


class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = ["id", "nome", "cpf", "dataNascimento"]

    def validate_cpf(self, cpf):
        if not cpf.isdecimal():
            raise ValidationError("CPF value should include only numbers")
        if len(cpf) != 11:
            raise ValidationError(f"CPF length should be 11 not {len(cpf)}")
        return cpf


class ContaSerializer(serializers.ModelSerializer):
    pessoa = serializers.SlugRelatedField(
        queryset=Pessoa.objects.all(), slug_field="id"
    )

    class Meta:
        model = Conta
        fields = "__all__"


class TransacaoSerializer(serializers.ModelSerializer):
    conta = serializers.SlugRelatedField(queryset=Conta.objects.all(), slug_field="id")

    class Meta:
        model = Transacao
        fields = "__all__"
