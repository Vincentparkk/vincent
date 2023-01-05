import base64       #인코딩과 디코딩 라이브러리
import hashlib
import hmac         #메시지 인증을 위한 키 해싱
import json
import time
import uuid
import httplib2
import CoinoneAPI_config
from CoinoneAPI_GET import GET
from pydantic import BaseModel
from typing import List, Optional

CoinoneAPI_config.config_generator()
ACCESS_TOKEN, SECRET_KEY = CoinoneAPI_config.config_read()
SECRET_KEY = bytes(SECRET_KEY, 'utf-8')

class Order(BaseModel):
    result: str
    error_code: str
    order_id: str

class Cancelorder(BaseModel):
    result: str
    error_code: str
    order_id: str
    price: str
    qty: str
    remain_qty: str
    side: str
    original_qty: str
    traded_qty: str
    canceled_qty: str
    fee: str
    fee_rate: str
    avg_price: str
    canceled_at: int
    ordered_at: int

class Cancelallorder(BaseModel):
    result: str
    error_code: str
    canceled_count: int
    total_order_count: int

class OpenInfo(BaseModel):
    order_id: str
    type: str
    quote_currency: str
    target_currency: str
    side: str
    price: str
    remain_qty: str
    original_qty: str
    canceled_qty: str
    executed_qty: str
    ordered_at: int
    fee: str
    fee_rate: Optional[str] = None
    average_executed_price: str
    feeRate: Optional[str] = None

class OpenOrder(BaseModel):
    result: str
    error_code: str
    open_orders: List[OpenInfo]

class Orderbase(BaseModel):
    order_id: str
    type: str
    quote_currency: str
    target_currency: str
    price: str
    original_qty: str
    executed_qty: str
    canceled_qty: str
    remain_qty: str
    status: str
    side: str
    fee: str
    fee_rate: str
    average_executed_price: str
    updated_at: int
    ordered_at: int


class OrderInfo(BaseModel):
    result: str
    error_code: str
    order: Orderbase
class POST():
    def __init__(self):
        self.ACCESS_TOKEN = ACCESS_TOKEN
        self.SECRET_KEY = SECRET_KEY

    def get_encoded_payload(self,payload):  # Parameter object -> JSON string -> base64
        '''V2는 nonce를 int로 넘겨줘야 한다.'''
        payload['nonce'] = int(time.time() * 1000)  # nonce는 랜덤의 정수

        dumped_json = json.dumps(payload)
        encoded_json = base64.b64encode(bytes(dumped_json, 'utf-8'))
        return encoded_json

    def get_encoded_payload_upgrade(self,payload):
        '''V2.1은 nonce를 str으로 넘겨줘야 한다.'''
        payload['nonce'] = str(uuid.uuid4())

        dumped_json = json.dumps(payload)
        encoded_json = base64.b64encode(bytes(dumped_json, 'utf-8'))
        return encoded_json

    def get_signature(self,encoded_payload):
        signature = hmac.new(SECRET_KEY, encoded_payload, hashlib.sha512)
        return signature.hexdigest()

    def get_response(self,action, payload):
        '''action는 받고 싶은 정보의 url의 뒷부분을 넣는다.
        payload는 access token 값을 넣는다.'''
        url = '{}{}'.format('https://api.coinone.co.kr/', action)

        if action[:4] == 'v2.1':
            encoded_payload =self.get_encoded_payload_upgrade(payload)
        else:
            encoded_payload = self.get_encoded_payload(payload)

        headers = {
            'Content-type': 'application/json',
            'X-COINONE-PAYLOAD': encoded_payload,
            'X-COINONE-SIGNATURE': self.get_signature(encoded_payload),
        }

        http = httplib2.Http()
        response, content = http.request(url, 'POST', body=encoded_payload, headers=headers)

        return content

    #place limit order
    #min_amount <= price * qty(수량) <= max_amount
    def place_limit_order(self,quote_currency='KRW',target_currency='BTC',side='BUY',price='0',qty='0.1',limit_order_type='LIMIT'):
        '''지정가 매수와 매도를 한다. 주문 방식은 LIMIT과 POST_ONLY가 있다.
        LIMIT은 지정가 주문이 체결 안되도 미체결로 둔다.
        POST_ONLY는 지정한 가격보다 낮은 가격에 체결되면 바로 취소된다.
        result: str
        error_code: str
        order_id: str'''
        data = json.loads(self.get_response(action='v2.1/order/limit', payload={
            'access_token': ACCESS_TOKEN,
            'quote_currency': quote_currency,  #통화 단위
            'target_currency': target_currency,   #종목
            'side': side,              #거래 유형
            'price': price,       #희망 거래 가격
            'qty': qty,               #거래 수량
            'limit_order_type': limit_order_type
        }))
        base = Order(**data)
        return base

    #주문 취소 -Cancel a single order
    #취소할 주문 정보
    def cancel_order(self,order_id='',quote_currency='KRW',target_currency='BTC'):
        '''특정 order_id를 가진 주문을 취소한다. target_currency는 무조건 입력해야한다.
        class Model(BaseModel):
        result: str
        error_code: str
        order_id: str
        price: str
        qty: str
        remain_qty: str
        side: str
        original_qty: str
        traded_qty: str
        canceled_qty: str
        fee: str
        fee_rate: str
        avg_price: str
        canceled_at: int
        ordered_at: int
        '''
        if order_id:
            data = json.loads(self.get_response(action='v2.1/order/cancel', payload={
            'access_token': ACCESS_TOKEN,
            'order_id':order_id,
            'quote_currency': quote_currency,
            'target_currency': target_currency,
            }))
            base = Cancelorder(**data)
            return base
        else:
            print("Input Order ID.")
        
    #주문취소-Cancel all orders for a specific trading pair
    def cancel_all_orders(self,quote_currency='KRW',target_currency='BTC'):
        '''target_currency의 모든 미체결 주문을 취소한다.
            result: str
            error_code: str
            canceled_count: int
            total_order_count: int'''
        data = json.loads(self.get_response(action='v2.1/order/cancel/all', payload={
            'access_token': ACCESS_TOKEN,
            'quote_currency': quote_currency,
            'target_currency': target_currency,
        }))
        base = Cancelallorder(**data)
        return base

    #open orders주문 대기 내역 조회하기-response: id, qty, fee, fee rate...
    def find_open_orders(self,quote_currency='KRW',target_currency='BTC'):
        '''특정 종목의 미체결된 주문들 확인하기
        result: str
        error_code: str
        open_orders: List[OpenInfo]
                        open_orders.order_id: str
                        type: str
                        quote_currency: str
                        target_currency: str
                        side: str
                        price: str
                        remain_qty: str
                        original_qty: str
                        canceled_qty: str
                        executed_qty: str
                        ordered_at: int
                        fee: str
                        fee_rate: Optional[str] = None
                        average_executed_price: str
                        feeRate: Optional[str] = None
        요금 정보를 가져오고 싶다 -> .open_orders[0].fee'''
        data = json.loads(self.get_response(action='v2.1/order/open_orders', payload={
            'access_token': self.ACCESS_TOKEN,
            'quote_currency': quote_currency,
            'target_currency': target_currency
            }))
        base = OpenOrder(**data)
        return base
    
    def find_all_open_orders(self):
        '''모든 종목의 미체결된 주문들 확인하기
            result: str
            error_code: str
            open_orders: List[OpenInfo]
                            open_orders.order_id: str
                            type: str
                            quote_currency: str
                            target_currency: str
                            side: str
                            price: str
                            remain_qty: str
                            original_qty: str
                            canceled_qty: str
                            executed_qty: str
                            ordered_at: int
                            fee: str
                            fee_rate: Optional[str] = None
                            average_executed_price: str
                            feeRate: Optional[str] = None
            요금 정보를 가져오고 싶다 -> .open_orders[0].fee'''
        data = json.loads(self.get_response(action='v2.1/order/open_orders/all', payload={
            'access_token': self.ACCESS_TOKEN
            }))
        base = OpenOrder(**data)
        return base
    
    def find_order_info(self,quote_currency='KRW', target_currency='BTC', order_id=''):
        '''order id에 대한 주문 정보를 확인한다.'''
        if order_id:
            data = json.loads(self.get_response(action='v2.1/order/info', payload={
                'access_token': self.ACCESS_TOKEN,
                'order_id': order_id,
                'quote_currency': quote_currency,
                'target_currency': target_currency,
            }))
            base = OrderInfo(**data)
            return base
        else:
            print("Wrong Order ID")

    def find_completed_orders(self,quote_currency='', target_currency='', size=30, from_ts = 1670016973000, to_ts = 1672816973000):
        '''완료된 주문에 대한 정보를 확인한다.
        quote_currency와 target_currency를 입력하면 해당 거래만 볼 수 있다.
        입력하지 않으면 모든 거래를 볼 수 있다.
        size는 [1,100]가능하다.'''
        if quote_currency and target_currency:
            print(f'{quote_currency} - {target_currency}의 완료된 주문 내역')
            print('-' * 20)
            pretty = json.loads(self.get_response(action='v2.1/order/completed_orders', payload={
                'access_token': self.ACCESS_TOKEN,
                'quote_currency': quote_currency,
                'target_currency': target_currency,
                'size': size,
                'from_ts': from_ts,
                'to_ts': to_ts,
                'to_trade_id': None
            }))
            print(json.dumps(pretty, ensure_ascii=False, indent=3))
            print('-' * 20)
        else:
            print('모든 종목의 완료된 주문 내역')
            print('-' * 20)
            pretty = json.loads(self.get_response(action='v2.1/order/completed_orders/all', payload={
                'access_token': self.ACCESS_TOKEN,
                'size': size,
                'from_ts': from_ts,
                'to_ts': to_ts,
                'to_trade_id': None
            }))
            print(json.dumps(pretty, ensure_ascii=False, indent=3))
            print('-' * 20)

    def get_coins_in_possession(self):
        '''보유하고 있는 원화와 코인들에 대한 정보만 출력한다.'''
        pretty = json.loads(self.get_response(action='v2/account/balance', payload={
            'access_token': self.ACCESS_TOKEN,
        }).decode('utf-8'))
        print('-' * 20)
        for i in pretty.keys():  # 계정이 가지고 있는 종목만 보기
            if i != "result" and i != "errorCode" and i != "normalWallets":
                if pretty[i]["avail"] != '0.0' or pretty[i]["balance"] != '0.0':
                    print("{}:\n  avail  : {}\n  balance: {}".format(i, pretty[i]["avail"], pretty[i]["balance"]))
        print('-' * 20)

    def get_deposit_address(self):
        '''소유하고 있는 코인의 지갑주소만 출력한다.'''
        pretty = json.loads(self.get_response(action='v2/account/deposit_address', payload={
            'access_token': self.ACCESS_TOKEN,
        }).decode('utf-8'))
        # print(json.dumps(pretty, sort_keys=True, indent=4))        #모든 코인의 지갑주소 출력. 없으면 null로 출력
        print('-' * 20)
        print("walletAddress")
        for i in pretty["walletAddress"].keys():
            if pretty["walletAddress"][i] != None:
                print("  {}: {}".format(i, pretty["walletAddress"][i]))
        print('-' * 20)

    def get_user_information(self):
        '''계정 소유자의 정보를 출력한다.'''
        pretty = json.loads(self.get_response(action='v2/account/user_info', payload={
            'access_token': self.ACCESS_TOKEN,
        }).decode('utf-8'))
        print('-' * 20)
        for i in pretty["userInfo"].keys():
            if i != "feeRate" and i != "securityLevel":  # 모든 fee rate를 보여주기 때문에 fee rate는 제외
                print(i)
                for j in pretty["userInfo"][i]:
                    print("  {}: {}".format(j, pretty["userInfo"][i][j]))
            elif i == "securityLevel":
                print("securityLevel\n  {}".format(pretty["userInfo"][i]))
        print('-' * 20)

if __name__ == "__main__":
    pass

