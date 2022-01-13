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
SESSION_VARIABLE_DURATION = 60
SESSION_VARIABLE_DURATION_TOLERANCE = 0.5

def getCurrencyRates(fiatCode, cryptoCode):
  pair = cryptoCode + fiatCode #XXBTZUSD
  url = 'https://api.kraken.com/0/public/Ticker?pair=' + pair

  headers = CaseInsensitiveDict()
  headers["Content-Type"] = "application/json"
  headers["Accept"] = "*/*"

  response = requests.get(url, headers=headers)
  result = response.json()
  rates = result["result"][pair]
  return {"rates": {
      "ask": rates["a"][0],
      "bid": rates["b"][0]
    }
  }

def ticker(fiatCode, cryptoCode):
  if (fiatCode == 'USD' or fiatCode == 'EUR'):
    return getCurrencyRates(fiatCode, cryptoCode)

  url = 'https://bitpay.com/api/rates'

  headers = CaseInsensitiveDict()
  headers["Content-Type"] = "application/json"
  headers["Accept"] = "*/*"

  response = requests.get(url, headers=headers)
  result = response.json()

  usdRate = None
  hnlRate = None
  for cambio in result:
    if cambio['code'] == 'USD':
      usdRate = float(cambio['rate'])
    elif cambio['code'] == 'HNL':
      hnlRate = float(cambio['rate'])
    
    if usdRate != None and hnlRate != None:
      break

  fxRate = hnlRate/usdRate  
  rates = getCurrencyRates('USD', cryptoCode)
  return {"rates": {
        "ask": float(rates["rates"]["ask"]) * fxRate,
        "bid": float(rates["rates"]["bid"]) * fxRate
      }
    }

def getConversion(criptomoneda):
  try:
    rates = ticker("HNL", criptomoneda)
    conversionA = float(rates["rates"]["ask"])
    conversionB = float(rates["rates"]["bid"])
    conversion = (conversionA + conversionB) / 2
    return conversion

  except Exception as e:
    print("error:", str(e))
    return {'error': str(e)}


def postTodoPago(lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC, tarjetaExpirationMonth, tarjetaExpirationYear, externalReference, email):
  try:
    responseLogin = postTodoPagoLogin()
    if responseLogin['status'] == 200:
      token = responseLogin['data']['token']
      responsePayDirect = postTodoPagoPayDirect(token, lempiras, tarjetaNumero, tarjetaNombre, tarjetaCVC,
                                                tarjetaExpirationMonth, tarjetaExpirationYear, externalReference, email)
      return responsePayDirect
    else:
      return {"error": "Se encontro un error en todo pago pay direct"}
  except Exception as e:
    print("ERROR4:", str(e))


def postTodoPagoLogin():
  try:
    urlLogin = env('URL_TODO_PAGO') + 'login'
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
                          tarjetaExpirationYear, externalReference, email):
  try:
    urlPayDirect = env('URL_TODO_PAGO') + 'direct-payment-without-register'
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Accept"] = "*/*"
    headers["X-Token"] = token
    headers["X-Tenant"] = "HNTP"
    headers["X-Content"] = "json"

    body = '{"accountNumber": "' + tarjetaNumero + '", "amount": ' + str(lempiras)
    body += ', "taxes": "0", "cardHolderName": "'
    body += tarjetaNombre + '", "comment": "Pago Directo ' + tarjetaNombre
    body += '", "commerceID": 429, "customerName": "' + tarjetaNombre
    body += '", "cvc": "' + str(tarjetaCVC)
    body += '", "expirationMonth": "' + tarjetaExpirationMonth
    body += '", "expirationYear": "' + tarjetaExpirationYear
    body += '", "externalReference": "' + str(externalReference) + '", "customerEmail": "' + email + '", "terminalNbr": "1"}'
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
    host = env('HOST_ELECTRUM')
    bodyPassword = env('PASSWORD_ELECTRUM_WALLET')
    public_key = env('PUBLIC_KEY_ELECTRUM')
    url = 'https://' + host + '/'
    
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    
    data = '{"jsonrpc":"2.0","id":"curltext","method":"payto","params":{"destination":"' + destination + '", "amount":"' + str(
      amount) + '", "password":"' + bodyPassword + '"}}'
    
    result = requests.post(url, headers=headers, data=data, verify=public_key)
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
    host = env('HOST_ELECTRUM')
    public_key = env('PUBLIC_KEY_ELECTRUM')
    url = 'https://' + host + '/'

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    data = '{"jsonrpc":"2.0","id":"curltext","method":"broadcast", "params":{"tx":"' + tx + '"}}'
    result = requests.post(url, headers=headers, data=data, verify=public_key)
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
    url = env('URL_TODO_PAGO') + "payment-reversal"
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


def set_expirable_var(session, var_name, value, set_at):
  session[var_name] = {'value': value, 'set_at': set_at}

def get_expirable_var(session, var_name, default=None):
  value = default
  if var_name in session:
    my_variable_dict = session.get(var_name, {})
    set_at = my_variable_dict.get('set_at', 0)
    difference = (datetime.now() - datetime.fromtimestamp(set_at, tz=None)).total_seconds()
    if difference <= (SESSION_VARIABLE_DURATION + SESSION_VARIABLE_DURATION_TOLERANCE):
      value = my_variable_dict.get('value')
  else:
    del session[var_name]
  return value
