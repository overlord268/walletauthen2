from django.db import transaction
from .forms import CompraForm
from django.views.generic import TemplateView
from .functions import postTodoPago, postElectrum
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect


class clsIndex(TemplateView):
  template_name = 'core/index.html'

  @staticmethod
  def post(request, *args, **kwargs):
    try:
      with transaction.atomic():
        if request.method == 'POST':
          form = CompraForm(request.POST)
          if form.is_valid():
            # TODOPAGO
            tarjetaExpiration = (form.cleaned_data['tarjeta_expiration_field']).split('/')
            tarjetaExpirationMonth = "".join(tarjetaExpiration[0].split())
            tarjetaExpirationYear = "".join(tarjetaExpiration[1].split())
            responseTodoPago = postTodoPago(
              form.cleaned_data['lempiras_field'],
              "".join(form.cleaned_data['tarjeta_numero_field'].split()),
              form.cleaned_data['tarjeta_nombre_field'],
              form.cleaned_data['tarjeta_cvc_field'],
              tarjetaExpirationMonth,
              tarjetaExpirationYear
            )
            print(responseTodoPago)
            if responseTodoPago['status'] == 200:
              # ELECTRUM
              res = postElectrum(form.cleaned_data['address_field'], form.cleaned_data['amount_field'])
              print("ELECTRUM POST", res)
              if res['error']:
                if 'HTTPConnectionPool' in res['error']:
                  # No se pudo conectar con el proveedor de la Wallet
                  messages.add_message(request, messages.ERROR,
                                       "Ocurrio un error en la Matrix | ERROR: 2")
                elif 'Insufficient funds' in res['error']['message']:
                  # Insuficientes fondos en Electrum Wallet
                  messages.add_message(request, messages.ERROR,
                                       "Ocurrio un error en la Matrix | ERROR: 1")

                else:
                  messages.add_message(request, messages.ERROR,
                                       "Ah ocurrido un error 2: {}".format(res['error']['message']))
              else:
                print('Entro 2')
                messages.add_message(request, messages.SUCCESS, "Se realizo el Post a electrum correctamente")
            else:
              messages.add_message(request, messages.ERROR,
                                   "Ah ocurrido un error 1: {}".format(responseTodoPago['message']))
            return redirect(reverse_lazy('home'))
        else:
          form = CompraForm()
          requestCopy = request.POST.copy()
    except Exception as e:
      messages.add_message(request, messages.ERROR,
                           "Ah ocurrido un error 3: {}".format(str(e)))
      return redirect(reverse_lazy('home'))

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['btc_products'] = [
      {"price": 3000},
      {"price": 2000},
      {"price": 1000},
      {"price": 500},
      {"price": 300},
      {"price": 200},
      {"price": 100}
    ]
    context['form'] = CompraForm

    return context
