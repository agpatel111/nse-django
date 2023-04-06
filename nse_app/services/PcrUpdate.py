import requests
import json
from Scheduler.CoustomFun import Coustom

def PcrUpdateFun(name):
    
    dict1 = {}
    
    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                'like Gecko) '
                                'Chrome/80.0.3987.149 Safari/537.36',
                'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + name

    response = requests.get(url, headers=headers)
    data = response.text
    api_data = json.loads(data)
    # -------------------------------------  API DATA   ---------------------------------------------------------
    timestamp = api_data['records']['timestamp']
    livePrice = api_data['records']['underlyingValue']
    filteredData = api_data['filtered']['data']
    
    down_price = Coustom.downPrice(filteredData, livePrice)

    up_price = Coustom.upPrice(filteredData, livePrice)
    
    downSliceList = Coustom.downMaxValue(down_price[:-6:-1])

    upSliceList = Coustom.upMaxValue(up_price[0:5])

    PEMax, PEMaxValue = Coustom.basePriceData(down_price[:-6:-1], downSliceList)
    
    CEMax, CEMaxValue = Coustom.resistancePriceData(up_price[0:5], upSliceList)    

    pcr = Coustom.pcrValue(api_data)


    dict1['livePrice'] = livePrice
    dict1['PEMax'] = PEMax
    dict1['CEMax'] = CEMax
    dict1['pcr'] = pcr
    return dict1