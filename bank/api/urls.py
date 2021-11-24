from django.urls import path
from api import views

urlpatterns = [
    path("pessoas/", views.pessoas, name="pessoas"),
    path("pessoa/<int:id>/", views.pessoas_detail, name="pessoa-detail"),
    path("contas/", views.contas, name="contas"),
    path("conta/<int:id>/", views.contas_detail, name="conta-detail"),
    path("conta/<int:id>/deposito/", views.deposito, name="deposito"),
    path("conta/<int:id>/saldo/", views.saldo, name="saldo"),
    path("conta/<int:id>/saque/", views.saque, name="saque"),
    path("conta/<int:id>/bloqueio/", views.bloqueio, name="bloqueio"),
    path("conta/<int:id>/desbloqueio/", views.desbloqueio, name="desbloqueio"),
    path("conta/<int:id>/transacoes/", views.transacoes, name="transacoes"),
]
