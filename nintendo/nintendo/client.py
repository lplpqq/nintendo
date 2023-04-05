import json
from typing import Optional, Dict, Any, Union

from bs4 import BeautifulSoup
from requests import Session
from requests.cookies import RequestsCookieJar

from .base import NintendoBase
from .models import Response, Profile, Tokens


CLIENT_ID = '01fe027acd6bc0cf'


class Nintendo(NintendoBase):
    def __init__(self, session: Optional[Session] = None):
        super(Nintendo, self).__init__(session)
        self.profile = None

    def authorize(self, cookies: Optional[Union[RequestsCookieJar, Dict[str, Any]]] = None) -> str:
        cookies = cookies or self.session.cookies
        if not cookies:
            raise ValueError('No cookies were set')

        params = {
            'client_id': CLIENT_ID,
            'state': '',
            'response_type': 'code id_token token',
            'scope': 'eshopDemo eshopDevice eshopPrice familyMember missionStatus missionStatus:progress openid parentalControlSetting pointTransaction pointWallet user user.birthday user.email user.membership user.mii user.wishlist',
            'redirect_uri': 'https://www.nintendo.com',
            'web_message_uri': 'https://accounts.nintendo.com',
            'web_message_target': 'op-frame',
            'response_mode': 'web_message',
            'prompt': 'none',
        }

        response = self._get('https://accounts.nintendo.com/connect/1.0.0/authorize', params=params, cookies=cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        state = json.loads(soup.find('div', id='state')['data-json'])
        user = state['user']

        self.profile = self.factory.load(
            user,
            Profile
        )

        tokens = self.factory.load(
            json.loads(soup.find('div', id='data')['data-json'])['responseParams'],
            Tokens
        )
        self.session.headers.update({
            'authorization': tokens.authorization_token,
            'x-access-token': tokens.access_token
        })
        return tokens.code

    def generate_tokens(self, authorization_code: str):
        json_data = {
            'operationName': 'GenerateTokens',
            'variables': {
                'code': authorization_code,
            },
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"156997112b4a81019a5706614b551e849f2ecc9a42558ea67d0f6985feb1939a"}}'
        }

        response = self._post('https://graph.nintendo.com/', model=Response, json=json_data)

        self.session.headers.update({
            'x-customer-token': response.data.tokens.customer_token
        })

    def retrieve_orders(self):
        params = {
            'operationName': 'CustomerOrderHistory',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"6b28b2a6bccc515fe4c7ff8de54774129500bf0e3d018a294aa5b726950b544d"}}',
        }

        orders_fetched, orders_total_number = 0, 1
        page_index = 1
        while orders_fetched < orders_total_number:
            variables = {
                "includeTotals": True,
                "page": page_index,
            }
            params['variables'] = json.dumps(variables)

            response = self._get('https://graph.nintendo.com/', model=Response, params=params)

            order_history = response.data.customer.order_history
            orders_total_number = order_history.totals.total_number
            orders = order_history.orders

            for order in orders:
                yield order

            page_index += 1
            orders_fetched += len(orders)
