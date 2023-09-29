from nse_app.models import *
from django.utils import timezone
import datetime
from datetime import datetime as dt
from datetime import date
import requests
import json
from datetime import timedelta
from rich.console import Console
from .CoustomFun import Coustom
from .SellFunction import sellFunOption



def BANKNIFTY():
    class InnerClass():
        def __init__(self, symbol = 'BANKNIFTY'):
            self.symbol = symbol
            self.headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
                'accept-language': 'en,gu;q=0.9,hi;q=0.8',
                'accept-encoding': 'gzip, deflate, br'
            }

        def fetch_data(self):
            url = f'https://www.nseindia.com/api/option-chain-indices?symbol={self.symbol}'
            response = requests.get(url, headers=self.headers).json()
            return response
        
        
    InnerClass_ = InnerClass()
    data = InnerClass_.fetch_data()
    print(data)