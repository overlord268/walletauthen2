import json
import requests
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import *
from requests.structures import CaseInsensitiveDict
from argon2 import PasswordHasher


class clsHome(TemplateView):
    template_name = 'core/index.html'

    def post(self, request, *args, **kwargs):
        try:
            res = json.loads(request.body)

            res.get('destination')
            res.get('amount')
            password = res.get('password')
            res.get('addtransaction')

            ph = PasswordHasher()
            hash = ph.hash(password)

            result = ph.verify(hash, password)
            print("Result ", result)
            print("Password", hash)

            url = "http://user:k1RIVG6tRhy9TQVANfBOng==@127.0.0.1:7777/"

            headers = CaseInsensitiveDict()
            headers["Authorization"] = "Basic dXNlcjpGbEJjYXFZNVo1c1liVzdYVDNMQU53PT0="
            headers["Content-Type"] = "application/json"

            data = '{"jsonrpc":"2.0","id":"curltext","method":"payto","params":{"destination":"' + res.get(
                'destination') + '", "amount":"' + res.get('amount') + '", "password":"' + res.get('password') + '"}}'
            print(data)
            resp = requests.post(url, headers=headers, data=data)

            print(resp.status_code)

        except Exception as e:
            print(e, "Error", str(e))

        return redirect(reverse_lazy('home'))
