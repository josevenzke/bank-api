from django.db import models
from django.db.models.deletion import CASCADE


class Pessoa(models.Model):
    nome = models.CharField(max_length=50)
    cpf = models.CharField(max_length=11, unique=True)
    dataNascimento = models.DateField()

    def __str__(self) -> str:
        return f"{self.nome}"


class Conta(models.Model):
    saldo = models.DecimalField(max_digits=11, decimal_places=2)
    limiteSaqueDiario = models.DecimalField(max_digits=11, decimal_places=2)
    flagAtivo = models.BooleanField(default=True)
    tipoConta = models.IntegerField(default=1)
    dataCriacao = models.DateTimeField(auto_now_add=True)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)


class Transacao(models.Model):
    valor = models.DecimalField(max_digits=11, decimal_places=2)
    dataTransacao = models.DateTimeField()
    conta = models.ForeignKey(Conta, on_delete=CASCADE)
