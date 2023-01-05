from pydantic import BaseModel
import requests
import json
import CoinoneAPI_config
from typing import List

CoinoneAPI_config.config_generator()
ACCESS_TOKEN, SECRET_KEY = CoinoneAPI_config.config_read()
SECRET_KEY = bytes(SECRET_KEY, 'utf-8')

class Chart(BaseModel):
    timestamp : str
    open : str
    high : str
    low : str
    close : str
    target_volume : str
    quote_volume : str

class Markets(BaseModel):

    quote_currency: str
    target_currency: str
    price_unit: str
    qty_unit: str
    max_order_amount: str
    max_price: str
    max_qty: str
    min_order_amount: str
    min_price: str
    min_qty: str
    order_book_units: list[str] = []
    maintenance_status: int
    trade_status: int
    order_types: list[str] = []

class Bid(BaseModel):
    price: str
    qty: str

class Ask(BaseModel):
    price: str
    qty: str

class Orderbooks(BaseModel):
    result: str
    error_code: str
    timestamp: int
    id: str
    quote_currency: str
    target_currency: str
    order_book_unit: str
    bids: List[Bid]
    asks: List[Ask]

class Currency(BaseModel):
    name: str
    symbol: str
    deposit_status: str
    withdraw_status: str
    deposit_confirm_count: int
    max_precision: int
    deposit_fee: str
    withdrawal_min_amount: str
    withdrawal_fee: str

class Ticker(BaseModel):
    quote_currency: str
    target_currency: str
    timestamp: int
    high: str
    low: str
    first: str
    last: str
    quote_volume: str
    target_volume: str
    best_asks: list[dict] = []
    best_bids: list[dict] = []
    id: str

class GET():
    def __init__(self):
        self._access_token = ACCESS_TOKEN
        self._secret_key = SECRET_KEY
        self._markets_info = {}
        self._tickers_info = {}

    def get_tickers(self, quote_currency = 'KRW', target_currency = ''):                          
        '''
        티커 조회(   quote_currency: str
                    target_currency: str
                    timestamp: int
                    high: str
                    low: str
                    first: str
                    last: str
                    quote_volume: str
                    target_volume: str
                    best_asks: list[dict] = []
                    best_bids: list[dict] = []
                    id: str)
        target을 입력하면 base를 return
        target을 입력하지 않으면 객체 데이터에 모든 tickers 저장
        '''
        url = "https://api.coinone.co.kr/public/v2/ticker_new/" + quote_currency
        if target_currency:
            url += '/' + target_currency
            params = {}
            response = requests.get(url, params=params)
            data = response.json()
            #print(json.dumps(data, sort_keys=True, indent=4))      #json형식 예쁘게 출력, 티커들의 간단한 정보 제공
            base = Ticker(**data["tickers"][0])
            return base
        else:
            params = {}
            response = requests.get(url, params=params)
            data = response.json()
            #print(json.dumps(data, sort_keys=True, indent=4))      #json형식 예쁘게 출력, 티커들의 간단한 정보 제공
            for i in range(len(data["tickers"])):
                self._tickers_info[data["tickers"][i]["target_currency"]] = Ticker(**data["tickers"][i])
            return self._tickers_info

    def get_markets(self, quote_currency = 'KRW', target_currency = ''):
        '''
        모든 종목들의 시장 거래 정보 조회, target_currency를 입력하면 해당 코인 정보만 조회
        quote_currency: str
        target_currency: str
        price_unit: str
        qty_unit: str
        max_order_amount: str
        max_price: str
        max_qty: str
        min_order_amount: str
        min_price: str
        min_qty: str
        order_book_units: list[str] = []
        maintenance_status: int
        trade_status: int
        order_types: list[str] = []'''
        url = "https://api.coinone.co.kr/public/v2/markets/" + quote_currency
        if target_currency:
            url += '/' + target_currency
            params = {}
            response = requests.get(url, params=params)
            data = response.json()
            #print(json.dumps(data, sort_keys=True, indent=4))
            base = Markets(**data["markets"][0])
            return base
        else:
            params = {}
            response = requests.get(url, params=params)
            data = response.json()
            #print(json.dumps(data, sort_keys=True, indent=4))
            for i in range(len(data["markets"])):
                self._markets_info[data["markets"][i]["target_currency"]] = Markets(**data["markets"][i])
            return self._markets_info

    def get_orderbook(self, quote_currency = 'KRW', target_currency = 'BTC', size = 15):
        '''오더북의 정보를 가져온다. size는 5, 10, 15만 가능하다. asks는 매도, bids는 매수
        result: str
        error_code: str
        timestamp: int
        id: str
        quote_currency: str
        target_currency: str
        order_book_unit: str
        bids: List[Bid]
        asks: List[Ask]'''
        url = "https://api.coinone.co.kr/public/v2/orderbook/" + quote_currency + '/' + target_currency
        params = {"size":size}
        response = requests.get(url, params=params)
        data = response.json()
        #print(json.dumps(data, sort_keys=True, indent=4))
        base = Orderbooks(**data)
        return base

    def get_recent_completed_orders(self, quote_currency = 'KRW', target_currency = 'BTC', size = 10):
        '''최근 주문에 대한 정보를 가져온다. size는 10, 50, 100, 150 ,200이다.'''
        url = "https://api.coinone.co.kr/public/v2/trades/" + quote_currency + '/' + target_currency
        params = {"size":size}
        response = requests.get(url, params=params)
        data = response.json()
        print(json.dumps(data, sort_keys=True, indent=4))
        return data

    def get_utc_ticker(self, quote_currency = 'KRW', target_currency = 'BTC'):
        '''
        utc는 협정세계시이다. 그냥 ticker랑 다른게 뭘까?'''
        url = "https://api.coinone.co.kr/public/v2/ticker_utc_new/" + quote_currency + '/' + target_currency
        params = {}
        response = requests.get(url, params=params)
        data = response.json()
        print(json.dumps(data, sort_keys=True, indent=4))
        return data

    def get_currencies(self, currency = 'BTC'):
        '''각 코인 및 통화에 대한 기본 정보를 가져온다.
            name: str
            symbol: str
            deposit_status: str
            withdraw_status: str
            deposit_confirm_count: int
            max_precision: int
            deposit_fee: str
            withdrawal_min_amount: str
            withdrawal_fee: str'''
        url = "https://api.coinone.co.kr/public/v2/currencies"
        if currency:                #잘못된 입력에 대해서 예외처리가 필요할까?
            url += '/' + currency
        params = {}
        response = requests.get(url, params=params)
        data = response.json()
        #print(json.dumps(data, sort_keys=True, indent=4))
        base = Currency(**data["currencies"][0])
        return base

    def get_chart(self, quote_currency = 'KRW', target_currency = 'BTC', interval = '1m', timestamp = ''):
        '''가장 최근의 1분봉 차트의 정보를 가져온다.
            timestamp : str
            open : str
            high : str
            low : str
            close : str
            target_volume : str
            quote_volume : str'''
        url = "https://api.coinone.co.kr/public/v2/chart/" + quote_currency + '/' + target_currency
        if timestamp:                #잘못된 입력에 대해서 예외처리가 필요할까?
            url += '/' + timestamp
        params = {"interval" :interval}
        response = requests.get(url, params=params)
        data = response.json()
        #print(json.dumps(data, sort_keys=True, indent=4))
        base = Chart(**data["chart"][0])
        return base

if __name__ == '__main__':
    coinone = GET()
    '''get_ticker'''
    #print(coinone.get_tickers(target_currency='BTC'))
    #coinone.get_tickers()
    #print(coinone._tickers_info['btc'])
    '''get_markets'''
    #print(coinone.get_markets(target_currency='BTC'))
    #coinone.get_markets()
    #print(coinone._markets_info['BTC'])
    '''get_orderbook'''
    #print(coinone.get_orderbook(target_currency='XRP').asks[1].price)
    '''get_recent_completed_orders'''
    #coinone.get_recent_completed_orders()
    '''get_utc_ticker'''
    #coinone.get_utc_ticker()
    '''get_currencies'''
    #print(coinone.get_currencies(currency='XRP').name)
    '''get_chart'''
    #print(coinone.get_chart(target_currency='XRP').open)
