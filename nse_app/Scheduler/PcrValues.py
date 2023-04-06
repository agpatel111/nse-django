import requests
import json
from nse_app.models import *
from CoustomFun import Coustom

def PcrValues():
    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                    'like Gecko) '
                    'Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
    response = requests.get(url, headers=headers)
    data = response.text
    api_data = json.loads(data)
    
    pcr = Coustom.pcrValue(api_data)
    
    pcr_values.objects.create(option_name='BANKNIFTY', pcr_value=pcr)
    print('Pcr BankNifty->', pcr)


    url_nifty = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    response_nifty = requests.get(url_nifty, headers=headers)
    data_nifty = response_nifty.text
    api_data_nifty = json.loads(data_nifty)
    
    pcr_nifty = Coustom.pcrValue(api_data_nifty)
    
    pcr_values.objects.create(option_name='NIFTY', pcr_value=pcr_nifty)
    print('Pcr Nifty->', pcr_nifty)