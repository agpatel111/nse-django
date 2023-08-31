import requests
import json
from nse_app.Scheduler.CoustomFun import Coustom
from nse_app.models import *

# def PcrUpdateFun(name):
    
#     dict1 = {}
    
#     headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
#                                 'like Gecko) '
#                                 'Chrome/80.0.3987.149 Safari/537.36',
#                 'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

#     url = 'https://www.nseindia.com/api/option-chain-indices?symbol=' + name

#     response = requests.get(url, headers=headers)
#     data = response.text
#     api_data = json.loads(data)
#     # -------------------------------------  API DATA   ---------------------------------------------------------
#     timestamp = api_data['records']['timestamp']
#     livePrice = api_data['records']['underlyingValue']
#     filteredData = api_data['filtered']['data']
    
#     down_price = Coustom.downPrice(filteredData, livePrice)

#     up_price = Coustom.upPrice(filteredData, livePrice)
    
#     downSliceList = Coustom.downMaxValue(down_price[:-6:-1])

#     upSliceList = Coustom.upMaxValue(up_price[0:5])

#     PEMax, PEMaxValue = Coustom.basePriceData(down_price[:-6:-1], downSliceList)
    
#     CEMax, CEMaxValue = Coustom.resistancePriceData(up_price[0:5], upSliceList)    

#     pcr = Coustom.pcrValue(api_data)


#     dict1['livePrice'] = livePrice
#     dict1['PEMax'] = PEMax
#     dict1['CEMax'] = CEMax
#     dict1['pcr'] = pcr
#     return dict1


def PcrUpdateFun():
    stock_url = 'https://zerodha.harmistechnology.com/stockname'
    stock_responce = requests.get(stock_url)
    stock_data = stock_responce.text
    stock_api_data = json.loads(stock_data)
    stock_for_buy.objects.filter(call_or_put='CALL').values()

    stocks = []
    for i in stock_api_data['data']:
        stocks.append(i['name'])
        
    stock_for_buy.objects.all().delete()
    
    update_needed = []
    success_count = 0
    reject_count = 0

    baseurl = "https://www.nseindia.com/"
    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) '
                         'Chrome/80.0.3987.149 Safari/537.36',
           'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    req = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(req.cookies)

    call_defs = []
    put_defs = []
    for stock in stocks:
        extra_setting.objects.filter(id = 1).update(pcr_isupdating = True)

        url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock
        try:
            response = requests.get(url, headers=headers, timeout=5, cookies=cookies)
            data = response.text
            api_data = json.loads(data)

            livePrice = api_data['records']['underlyingValue']
            filteredData = api_data['filtered']['data']

            pcr = Coustom.pcrValue(api_data)
            down_price = Coustom.downPrice(filteredData, livePrice)
            up_price = Coustom.upPrice(filteredData, livePrice)
            downSliceList = Coustom.downMaxValue(down_price[:-6:-1])
            upSliceList = Coustom.upMaxValue(up_price[0:5])
            PEMax, PEMaxValue = Coustom.basePriceData(down_price[:-6:-1], downSliceList)
            CEMax, CEMaxValue = Coustom.resistancePriceData(up_price[0:5], upSliceList)
            
            ## Down Side
            CE__fist_down = down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest']
            PE__fist_down = down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']
            PE_side_persnt = float('%.2f'% ((CE__fist_down / PE__fist_down) * 100))

            ## Up side
            CE__fist_Up = up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest']
            PE__fist_Up = up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']
            CE_side_persnt = float('%.2f'% ((PE__fist_Up / CE__fist_Up) * 100))
            
            
            ### CALLL
            if down_price[-1]['strikePrice'] == PEMaxValue[0]:            
                pe_ce_Diff = True
                pe = False
                arr_up = []
                for uppppp in up_price[0:2]:
                    up_ = (uppppp['PE']['changeinOpenInterest'] + uppppp['PE']['openInterest']) - (uppppp['CE']['changeinOpenInterest'] + uppppp['CE']['openInterest'])
                    arr_up.append(up_)
                sum_up = abs(arr_up[0] + arr_up[1])
                up_base_total = (down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']) - (down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest'])
                if up_base_total > sum_up:
                    call_defs.append({"sum": up_base_total - sum_up, 'StockName': stock })
                    print(stock,up_base_total - sum_up)
                    stock_for_buy.objects.create(stocks_name=stock, call_or_put='CALL', difference_ce_pe=up_base_total - sum_up, PE_side_persnt = PE_side_persnt, CE_side_persnt = CE_side_persnt)            
            
            #### PUT
            elif up_price[0]['strikePrice'] == CEMaxValue[0]:
                pe_ce_Diff = True
                pe = True

                arr_down = []
                for downnnn in down_price[:-3:-1]:
                    down_ = (downnnn['PE']['changeinOpenInterest'] + downnnn['PE']['openInterest']) - (downnnn['CE']['changeinOpenInterest'] + downnnn['CE']['openInterest'])
                    arr_down.append(down_)
                sum_down = (arr_down[0] + arr_down[1])
                sum_down = abs(sum_down)
                down_base_total = (up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']) - (up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest'])
                down_base_total = abs(down_base_total)
                if (down_base_total) > (sum_down):
                    if pcr <= 0.67:
                        put_defs.append({"sum": down_base_total - sum_down, 'StockName': stock})
                        # print(stock, down_base_total - sum_down)
                        stock_for_buy.objects.create(stocks_name=stock, call_or_put='PUT', difference_ce_pe=down_base_total - sum_down,PE_side_persnt = PE_side_persnt ,CE_side_persnt = CE_side_persnt)            

            else:
                pe_ce_Diff = False
                pe = False

            payload = {'name': stock, 'pcr': pcr, 'PE_CE_diffrent': pe_ce_Diff, 'CE': pe_ce_Diff, 'PE': pe}
            requests.put(
                "https://zerodha.harmistechnology.com/stockname", data=payload)
            success_count = success_count + 1
            # pcr_stock_name.objects.filter(name = stock).update(pcr =  pcr)
            print(stock, '->',pcr, '->', pe_ce_Diff)
            if stock == 'NO DATA':
                extra_setting.objects.filter(id = 1).update(pcr_isupdating = False)
        except Exception as e:
            print('Error-->',e)
            print('An exception occurred','->', stock)
            extra_setting.objects.filter(id = 1).update(pcr_isupdating = False)
            update_needed.append(stock)
            reject_count = reject_count + 1
            
    # sorted_call = sorted(call_defs, key=lambda i: -i['sum'])
    # sorted_put = sorted(put_defs, key=lambda j: -j['sum'])
    # if len(sorted_call) != 0:
    #     pass
    #     # stock_for_buy.objects.create(stocks_name=sorted_call[0]['StockName'], call_or_put='CALL')
    # if len(sorted_put) != 0: 
    #     pass   
    #     # stock_for_buy.objects.create(stocks_name=sorted_put[0]['StockName'], call_or_put='PUT')
    return update_needed, success_count, reject_count