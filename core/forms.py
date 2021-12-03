from django import forms

class CompraForm(forms.Form):
  address_field = forms.CharField(label='Address', max_length=100)
  amount_field = forms.FloatField(label='Amount')
  lempiras_field = forms.FloatField(label='Lempiras')
  tarjeta_numero_field = forms.CharField(label='Numero de la tarjeta')
  tarjeta_nombre_field = forms.CharField(label='Nombre en la tarjeta')
  tarjeta_cvc_field = forms.IntegerField(label='CVC')
  tarjeta_expiration_field = forms.CharField(label='Fecha de caducidad')
  