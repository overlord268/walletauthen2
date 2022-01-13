import datetime
from django.db import transaction
from .forms import CompraForm
from django.views.generic import TemplateView, View
from .functions import postTodoPago, postElectrum, getConversion, set_expirable_var, get_expirable_var
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from .models import Transaccion, Estado
from register.models import Customer
from django.http import JsonResponse


class clsIndex(TemplateView):
  template_name = 'core/index.html'
  form_class = CompraForm
  initial = {'key': 'value'}
  esperar_verificacion = False
  btc_products = [
    {"price": 3000},
    {"price": 2000},
    {"price": 1000},
    {"price": 500},
    {"price": 300},
    {"price": 200},
    {"price": 100}
  ]

  def get(self, request):
    form = self.form_class(initial=self.initial)
    #current_user = request.user
    #current_customer = Customer.objects.get(user=current_user)
    # if current_customer.numero_ID == None:
    #  self.esperar_verificacion = True
    return render(request, self.template_name, {'form': form, 'btc_products': self.btc_products, 'esperar_verificacion': self.esperar_verificacion})

  def post(self, request, *args, **kwargs):
    try:
      current_user = request.user
      current_customer = Customer.objects.get(user=current_user)
      #if current_customer.numero_ID == None:
      #  self.esperar_verificacion = True
      with transaction.atomic():
        form = self.form_class(request.POST)
        if form.is_valid():
          lempiras = form.cleaned_data['lempiras_field']
          cambio = get_expirable_var(request.session, 'conversion_btc_hnl')
          if cambio == None:
            cambio = getConversion('XXBTZ')
          btc = round((float(lempiras) / cambio), 8)
          wallet_address = form.cleaned_data['address_field']
          
          tarjeta_numero = "".join(form.cleaned_data['tarjeta_numero_field'].split())
          tarjeta_nombre = form.cleaned_data['tarjeta_nombre_field']
          tarjeta_cvc = form.cleaned_data['tarjeta_cvc_field']
          tarjetaExpiration = (form.cleaned_data['tarjeta_expiration_field']).split('/')
          tarjetaExpirationMonth = "".join(tarjetaExpiration[0].split())
          tarjetaExpirationYear = "".join(tarjetaExpiration[1].split())

          #DB
          estados = Estado.objects.all()
          tx = Transaccion(amount_hnl=float(lempiras), amount_btc=float(btc), 
            wallet_address=str(wallet_address), btc_hnl_change=float(cambio), 
            transaction_id_todopago='', transaction_id_electrum='', estado=estados.get(idEstado=1), 
            customer=current_customer)

          tx.save()

          # TODOPAGO
          responseTodoPago = postTodoPago(
            lempiras,
            tarjeta_numero,
            tarjeta_nombre,
            tarjeta_cvc,
            tarjetaExpirationMonth,
            tarjetaExpirationYear,
            'lb-' + str(tx.idTransaccion), 
            current_user.email
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
                                  "Ha ocurrido un error 1: {}".format(responseTodoPago['error']))
          return redirect(reverse_lazy('home'))
        return render(request, self.template_name, {'form': form, 'btc_products': self.btc_products, 'esperar_verificacion': self.esperar_verificacion})
    except Exception as e:
      print("EXCEPTION: ", str(e))
      messages.add_message(request, messages.ERROR,
                           "Ha ocurrido un error en la Matrix: {}".format(str(e)))
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

class conversionBtcHnl(View):
  acceptedCrypto = ['XXBTZ', 'XLTCZ']

  def get(self, request):
    crypto = 'XXBTZ'
    if 'crypto' in request.GET:
      crypto = request.GET['crypto']
    
    if crypto in self.acceptedCrypto:
      cambio = getConversion(crypto)
      cambio_compra = cambio + 0.1 * cambio
      cambio_venta = cambio - 0.1 * cambio
      
      set_at = datetime.datetime.now().timestamp()
      set_expirable_var(request.session, 'conversion_btc_hnl', cambio, set_at)

      return JsonResponse({'conversion': cambio_compra, 'conversion1': cambio_venta})
    else:
      return JsonResponse({'error': 'error'})
