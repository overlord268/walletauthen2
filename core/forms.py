from django import forms

class CompraForm(forms.Form):
  address_field = forms.CharField(label='Dirección de la billetera', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Dirección de la billetera', 'class': 'form-control'}))
  amount_field = forms.FloatField(label='Bitcoin', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
  lempiras_field = forms.FloatField(label='Lempiras', widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}))
  cambio_btc_lempiras = forms.FloatField(label='Cambio', required=False, widget=forms.HiddenInput(attrs={'class': 'form-control'}))
  tarjeta_numero_field = forms.CharField(label='Numero de la tarjeta', widget=forms.TextInput(attrs={'placeholder': '0000 0000 0000 0000', 'class': 'form-control'}))
  tarjeta_nombre_field = forms.CharField(label='Nombre en la tarjeta', widget=forms.TextInput(attrs={'placeholder': 'Ingrese su nombre', 'class': 'form-control'}))
  tarjeta_cvc_field = forms.IntegerField(label='CVC', widget=forms.TextInput(attrs={'placeholder': '123', 'class': 'form-control'}))
  tarjeta_expiration_field = forms.CharField(label='Fecha de caducidad', widget=forms.TextInput(attrs={'placeholder': 'MM/AA', 'class': 'form-control'}))
  