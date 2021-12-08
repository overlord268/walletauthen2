from datetime import datetime
from requests.structures import CaseInsensitiveDict
from django.http import HttpResponseRedirect, JsonResponse
from pathlib import Path
import os, environ, requests

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))


def postTodoPago(lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC, tarjetaExpirationMonth, tarjetaExpirationYear):
  try:
    responseLogin = postTodoPagoLogin()
    if responseLogin['status'] == 200:
      token = responseLogin['data']['token']
      responsePayDirect = postTodoPagoPayDirect(token, lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC,
                                                tarjetaExpirationMonth, tarjetaExpirationYear)
      print("RESPONSE PAYDIRECT", responsePayDirect)
      return responsePayDirect
    else:
      return {"error": "Se encontro un error en todo pago pay direct"}
  except Exception as e:
    print("ERROR4:", str(e))


def postTodoPagoLogin():
  try:
    urlLogin = 'https://preprod-api.todopago.hn/pay/v1/login'
    user = env('USER_TODO_PAGO')
    password = env('PASSWORD_TODO_PAGO')

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    headers["X-Tenant"] = "HNTP"

    body = '{"user":"' + user + '", "password":"' + password + '"}'

    result = requests.post(urlLogin, headers=headers, data=body)
    res = result.json()
    if res['status'] == 200:
      return res
    else:
      return {'error': res['message']}

  except Exception as e:
    print("error:", str(e))
    return {'error': str(e)}


def postTodoPagoPayDirect(token, lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC, tarjetaExpirationMonth,
                          tarjetaExpirationYear):
  try:
    urlPayDirect = 'https://preprod-api.todopago.hn/pay/v1/direct-payment-without-register'

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    headers["X-Token"] = token
    headers["X-Tenant"] = "HNTP"
    headers["X-Content"] = "json"

    now = datetime.now()
    externalReference = "".join(tarjetaNombre.split()) + "-" + now.strftime('%d-%m-%Y-%H:%M')

    body = '{"accountNumber": "' + tarjetaNumero + '", "amount": ' + str(lempiras)
    body += ', "taxes": "15", "cardHolderName": "'
    body += tarjetaNombre + '", "comment": "Pago Directo ' + tarjetaNombre
    body += '", "commerceID": 429, "customerName": "' + tarjetaNombre
    body += '", "cvc": "' + str(tarjetaCVC)
    body += '", "expirationMonth": "' + tarjetaExpirationMonth
    body += '", "expirationYear": "' + tarjetaExpirationYear
    body += '", "externalReference": "' + externalReference + '", "customerEmail": "dtejada@isonet-globalsys.com", "terminalNbr": "1"}'

    result = requests.post(urlPayDirect, headers=headers, data=body)
    res = result.json()
    if res['status'] == 200:
      print("Done, Status 200")
      return res
    else:
      print("ERROR POST TODO PAGO:", res['message'])
      return {'error': res['message']}

  except Exception as e:
    print("ERROR2:", str(e))
    return {'error': str(e)}


def postElectrum(destination, amount):
  try:
    user = env('USER_ELECTRUM')
    password = env('PASSWORD_ELECTRUM')
    host = '127.0.0.1'
    port = '7777'
    bodyPassword = env('PASSWORD_ELECTRUM_WALLET')

    url = 'http://' + user + ':' + password + '@' + host + ':' + port + '/'
    headers = CaseInsensitiveDict()
    headers["Authorization"] = "Basic {}".format(env('PASSWORD_ELECTRUM'))
    headers["Content-Type"] = "application/json"

    data = '{"jsonrpc":"2.0","id":"curltext","method":"payto","params":{"destination":"' + destination + '", "amount":"' + str(
      amount) + '", "password":"' + bodyPassword + '"}}'

    result = requests.post(url, headers=headers, data=data)
    res = result.json()
    print("POST ELECTRUM ERROR: ", res)
    return res

  except Exception as e:
    return {'error': str(e)}