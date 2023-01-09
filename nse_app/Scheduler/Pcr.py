import requests
import json
from datetime import time
from django.shortcuts import render


def pcr(request):

    stock_url = 'https://zerodha.harmistechnology.com/stockname'
    stock_responce = requests.get(stock_url)
    stock_data = stock_responce.text
    stock_api_data = json.loads(stock_data)
    # pprint.pprint(stock_api_data['data'])
    stocks = []
    for i in stock_api_data['data']:
        stocks.append(i['name'])
    print(stocks[:15])

    update_needed = []

    # stocks = ['TCS', 'IDFC', 'ABB', 'ACC', 'DLF', 'HAL', 'TITAN', 'SBIN', 'AXISBANK']
    for stock in stocks[:15]:
        url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                   'accept-language': 'en,gu;q=0.9,hi;q=0.8',
                   'accept-encoding': 'gzip, deflate, br',
                   'upgrade-insecure-requests': '1'
                   }
        try:
            response = requests.get(url, headers=headers)
            data = response.text
            api_data = json.loads(data)
            print('------------------------------------------------------------------------------------------------------------')
            sum = api_data['filtered']['CE']['totOI']
            sum2 = api_data['filtered']['PE']['totOI']
            pcr = '%.2f' % (sum2 / sum)
            # pcr_stock_name.objects.filter(name = stock).update(pcr =  pcr)
            print(pcr)
            print(stock)
            time.sleep(5)
        except:
            print('An exception occurred')
            update_needed.append(stock)
            print(stock)
            time.sleep(5)
    return render(request, "demo.html", {'update_needed': update_needed})