from django.db import models

class Transaccion(models.Model):
  id = models.BigAutoField(primary_key=True)
  amount_hnl = models.FloatField()
  amount_btc = models.FloatField()
  wallet_address = models.CharField(max_length=40)
  btc_hnl_change = models.FloatField()
  transaction_id_todopago = models.CharField(max_length=100)
  fecha_hora = models.DateTimeField(auto_now_add=True)
  estado = models.ForeignKey('Estado')

class Estado(models.Model):
  id = models.BigAutoField(primary_key=True)
  name = models.CharField(max_length=50)
