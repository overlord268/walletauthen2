from django.db import transaction
from .forms import CompraForm
from django.views.generic import TemplateView
from .functions import postTodoPago, postElectrum
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from .models import Transaccion, Estado


class clsIndex(TemplateView):
  template_name = 'core/index.html'

  @staticmethod
  def post(request, *args, **kwargs):
    try:
      with transaction.atomic():
        if request.method == 'POST':
          form = CompraForm(request.POST)
          if form.is_valid():
            lempiras = form.cleaned_data['lempiras_field']
            btc = form.cleaned_data['amount_field']
            wallet_address = form.cleaned_data['address_field']
            cambio = form.cleaned_data['cambio_btc_lempiras']
            tarjeta_numero = "".join(form.cleaned_data['tarjeta_numero_field'].split())
            tarjeta_nombre = form.cleaned_data['tarjeta_nombre_field']
            tarjeta_cvc = form.cleaned_data['tarjeta_cvc_field']
            tarjetaExpiration = (form.cleaned_data['tarjeta_expiration_field']).split('/')
            tarjetaExpirationMonth = "".join(tarjetaExpiration[0].split())
            tarjetaExpirationYear = "".join(tarjetaExpiration[1].split())

            #DB
            estados = Estado.objects.all()
            for i in estados:
              print('Estado es>', i)
            tx = Transaccion(amount_hnl=float(lempiras), amount_btc=float(btc), 
              wallet_address=str(wallet_address), btc_hnl_change=float(cambio), 
              transaction_id_todopago='', transaction_id_electrum='', estado=estados.get(idEstado=1))

            tx.save()

            # TODOPAGO
            responseTodoPago = postTodoPago(
              lempiras,
              tarjeta_numero,
              tarjeta_nombre,
              tarjeta_cvc,
              tarjetaExpirationMonth,
              tarjetaExpirationYear,
              'lb-' + str(tx.idTransaccion)
            )
            print("Todo Pago: ", responseTodoPago)
            if 'res' in responseTodoPago:
              if responseTodoPago['res']['status'] == 200:
                #DB
                tx.transaction_id_todopago = str(responseTodoPago['res']['data']['transaccionID'])
                tx.estado = estados.get(idEstado=2)
                tx.save()

                # ELECTRUM
                print("BTC AMOUNT: ", form.cleaned_data['amount_field'])
                res = postElectrum(
                  wallet_address,
                  btc,
                  responseTodoPago['token'],
                  responseTodoPago['res']['data']['transaccionID'],
                  responseTodoPago['externalReference']
                )

                print("postElectrum_res: ", res)

                if 'error' in res:
                  if 'HTTPConnectionPool' in res['error']:
                    # No se pudo conectar con el proveedor de la Wallet
                    tx.estado = estados.get(idEstado=5)
                    tx.save()
                    messages.add_message(request, messages.ERROR,
                                        "Ocurrio un error en la Matrix | ERROR: 1")
                  elif 'Insufficient funds' in res['error']['message']:
                    # Insuficientes fondos en Electrum Wallet
                    tx.estado = estados.get(idEstado=6)
                    tx.save()
                    messages.add_message(request, messages.ERROR,
                                        "Ocurrio un error en la Matrix | ERROR: 2")
                  else:
                    tx.estado = estados.get(idEstado=7)
                    tx.save()
                    messages.add_message(request, messages.ERROR,
                                        "Ocurrido un error en la Matrix: ERROR 3")
                elif 'paymentReversal' in res:
                  tx.estado = estados.get(idEstado=8)
                  tx.save()
                  messages.add_message(request, messages.SUCCESS, "Ocurrio un error, se devolvieron sus fondos")
                else:
                  tx.transaction_id_electrum = res['result']
                  tx.estado = estados.get(idEstado=3)
                  tx.save()
                  messages.add_message(request, messages.SUCCESS, "Se realizo el pago correctamente")
                  ## Aqui va

            else:
              tx.estado = estados.get(idEstado=4)
              tx.save()
              messages.add_message(request, messages.ERROR,
                                   "Ha ocurrido un error 1: {}".format(responseTodoPago['error']['message']))
            return redirect(reverse_lazy('home'))
        else:
          form = CompraForm()
          requestCopy = request.POST.copy()
          return requestCopy
    except Exception as e:
      print("EXCEPTION: ", str(e))
      messages.add_message(request, messages.ERROR,
                           "Ocurrido un error en la Matrix: {}".format(str(e)))
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
