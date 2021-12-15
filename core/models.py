from django.db import models

class Transaccion(models.Model):
  idTransaccion = models.BigAutoField(db_column='idTransaccion', primary_key=True)
  amount_hnl = models.FloatField()
  amount_btc = models.FloatField()
  wallet_address = models.CharField(max_length=255)
  btc_hnl_change = models.FloatField()
  transaction_id_todopago = models.CharField(max_length=255)
  transaction_id_electrum = models.CharField(max_length=255)
  fecha_hora = models.DateTimeField(auto_now_add=True)
  estado = models.ForeignKey('Estado', models.DO_NOTHING, db_column='idEstado')

  def __str__(self):
    return '{}'.format(self.idTransaccion)

class Estado(models.Model):
  idEstado = models.BigAutoField(primary_key=True, db_column='idEstado')
  name = models.CharField(max_length=50)
  descripcion = models.CharField(max_length=150)

  def __str__(self):
    return '{} - {} - {}'.format(self.idEstado, self.name, self.descripcion)
