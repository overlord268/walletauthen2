import environ
import os
import requests
from datetime import datetime
from pathlib import Path
from requests.structures import CaseInsensitiveDict

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
token = ""
transactionID = ""
externalReference = ""

def getConversion(criptomoneda):
  try:
    url = 'https://bitpay.com/api/rates/' + criptomoneda
    
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    
    result = requests.get(url, headers=headers)
    res = result.json()
    res_dict = dict(enumerate(res))
    if result.status_code == 200:
      conversion = float(res_dict[68]['rate'])
      conversion += 0.1 * conversion
      return float(conversion)
    else:
      return {'error': 'error'}

  except Exception as e:
    print("error:", str(e))
    return {'error': str(e)}

def postTodoPago(lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC, tarjetaExpirationMonth, tarjetaExpirationYear, externalReference):
  try:
    responseLogin = postTodoPagoLogin()
    if responseLogin['status'] == 200:
      token = responseLogin['data']['token']
      responsePayDirect = postTodoPagoPayDirect(token, lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC,
                                                tarjetaExpirationMonth, tarjetaExpirationYear, externalReference)
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
    print("postTodoPagoLogin_res: ", res)
    if res['status'] == 200:
      return res
    else:
      return {'error': res['message']}

  except Exception as e:
    print("error:", str(e))
    return {'error': str(e)}


def postTodoPagoPayDirect(token, lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC, tarjetaExpirationMonth,
                          tarjetaExpirationYear, externalReference):
  try:
    urlPayDirect = 'https://preprod-api.todopago.hn/pay/v1/direct-payment-without-register'
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    headers["X-Token"] = token
    headers["X-Tenant"] = "HNTP"
    headers["X-Content"] = "json"
    now = datetime.now()
    # externalReference = "".join(tarjetaNombre.split()) + "-" + now.strftime('%d-%m-%Y-%H:%M')
    body = '{"accountNumber": "' + tarjetaNumero + '", "amount": ' + str(lempiras)
    body += ', "taxes": "0", "cardHolderName": "'
    body += tarjetaNombre + '", "comment": "Pago Directo ' + tarjetaNombre
    body += '", "commerceID": 429, "customerName": "' + tarjetaNombre
    body += '", "cvc": "' + str(tarjetaCVC)
    body += '", "expirationMonth": "' + tarjetaExpirationMonth
    body += '", "expirationYear": "' + tarjetaExpirationYear
    body += '", "externalReference": "' + str(externalReference) + '", "customerEmail": "dtejada@isonet-globalsys.com", "terminalNbr": "1"}'
    result = requests.post(urlPayDirect, headers=headers, data=body)
    res = result.json()
    print("postTodoPagoPayDirect_res: ", res)
    if res['status'] == 200:
      return {"res": res, "token": token, "externalReference": externalReference}
    else:
      return {'error': res['message']}

  except Exception as e:
    print("ERROR2:", str(e))
    return {'error': str(e)}


def postElectrum(destination, amount, tokenID, transactionID, externalReference):
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
    print("postElectrum_res: ", res)
    if "error" in res:
      resPaymentReversal = postPaymentReversal(tokenID, transactionID, externalReference)
      return resPaymentReversal
    else:
      resB = postElectrumBroadcast(res['result'])
      return resB

  except Exception as e:
    return {'error': str(e)}


def postElectrumBroadcast(tx):
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
    data = '{"jsonrpc":"2.0","id":"curltext","method":"broadcast", "params":{"tx":"' + tx + '"}}'
    result = requests.post(url, headers=headers, data=data)
    res = result.json()
    print("postElectrumBroadcast_res: ", res)
    if "error" in res:
      resPaymentReversal = postPaymentReversal(token, transactionID, externalReference)
      return resPaymentReversal
    else:
      return res

  except Exception as e:
    return {'error': str(e)}


def postPaymentReversal(tokenID, transactionID, externalReference):
  try:
    url = "https://preprod-api.todopago.hn/pay/v1/payment-reversal"
    headers = CaseInsensitiveDict()
    headers["Accept"] = "application/json"
    headers["X-Token"] = "{}".format(str(tokenID))
    headers["X-Tenant"] = "HNTP"
    headers["X-Content"] = "json"
    headers["Content-Type"] = "application/json"
    data = '{"transactionID": "' + str(transactionID) + '","externalReference": "' + str(externalReference) + '"}'
    resp = requests.post(url, headers=headers, data=data)
    res = resp.json()
    print("postPaymenReversal_res:", res)
    if res['status'] == 200:
      return {"paymentReversal": res}
    else:
      return {'error': res['message']}
  except Exception as e:
    return {'error': str(e)}