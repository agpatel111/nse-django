from nse_app.models import *
import requests
import json
from django.utils import timezone
from rich.console import Console
from .CoustomFun import Coustom
from.SellFunction import sellFunStock, futureStockLivePrice

## StockPcrCAllPut Code is in document folder

consoleYellow = Console(style='yellow')
consoleRed = Console(style='red')
consoleBlue = Console(style='blue')
consoleGreen = Console(style='green')

STOCK_URL = 'https://www.nseindia.com/api/option-chain-equities?symbol='

def stockFutureSell():
    try:
        def apiData(stock):
            baseurl = "https://www.nseindia.com/"
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ''like Gecko) ''Chrome/80.0.3987.149 Safari/537.36','accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
            session = requests.Session()
            req = session.get(baseurl, headers=headers, timeout=5)
            cookiess = dict(req.cookies)
            
            url = STOCK_URL + stock
            response = requests.get(url, headers=headers, cookies=cookiess, timeout=5).json()
            
            return response

        
        stock_details = stock_detail.objects.values().order_by("-buy_time")[:50]
        nseSetting = nse_setting.objects.values()
        
        for setting in nseSetting: 
            if setting['option'] == 'STOCK FUTURE':       ## Name as per Local DB
                OptionId_Future = setting['id']
                
                
        for sell in stock_details:
            ## FUTURE SELL
            if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_Future:
                sell_time = timezone.now()
                if sell['base_strike_price']: 
                    strikePrice = sell['base_strike_price']
                else:
                    strikePrice = 0
                    
                stockName = sell['stock_name']
                id = sell['id']
                buy_price = sell['buy_price']
                sell_price = sell['sell_price']
                stop_loseprice = sell['stop_loseprice']
                futureLive = futureStockLivePrice(stockName)
                api_data = apiData(stockName)
                # filteredData = api_data['filtered']['data']
                pcr = Coustom.pcrValue(api_data)
                
                if sell['type'] == 'BUY':
                    consoleGreen.print(f'{stockName} FUTURE BUY--->', 'enrty price:', buy_price, 'target_price:', sell_price, 'liveBidPrice:', futureLive, 'stop_Loss:', stop_loseprice)
                    if sell_price <= futureLive :
                        final_status = "PROFIT"
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                        consoleYellow.print(f"Successfully SELL STOCK OF {stockName} FUTURE")
                    if stop_loseprice >= futureLive:
                        final_status = "LOSS"
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                        consoleYellow.print(f"Successfully SELL STOCK OF {stockName} FUTURE")
                    if sell['admin_call'] == True:
                        if buy_price <= futureLive:
                            final_status = 'PROFIT'
                        else:
                            final_status = 'LOSS'
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                        consoleYellow.print(f"Successfully SELL STOCK OF {stockName} FUTURE")
                elif sell['type'] == 'SELL':
                    consoleGreen.print(f'{stockName} FUTURE SELL--->', 'enrty price:', buy_price, 'target_price:', sell_price, 'liveBidPrice:', futureLive, 'stop_Loss:', stop_loseprice)
                    if sell_price >= futureLive :
                        final_status = "PROFIT"
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                        consoleYellow.print(f"Successfully SELL STOCK OF {stockName} FUTURE")
                    if stop_loseprice <= futureLive:
                        final_status = "LOSS"
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                        consoleYellow.print(f"Successfully SELL STOCK OF {stockName} FUTURE")
                    if sell['admin_call'] == True:
                        if buy_price > futureLive:
                            final_status = 'PROFIT'
                        else:
                            final_status = 'LOSS'
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                        consoleYellow.print(f"Successfully SELL STOCK OF {stockName} FUTURE")
    except Exception as e:
        print('Error-->', e)
        print("Connection refused by the server........................................ STOCK")


# def StockCall():
#     PcrIsUpdating = extra_setting.objects.filter(id = 1).values()
#     if PcrIsUpdating[0]['pcr_isupdating'] == True :
#         consoleRed.print("Pcr is Updating Please Wait")
#     else:
#         try:
#             settings_url = 'https://zerodha.harmistechnology.com/setting_nse'
#             response = requests.get(settings_url)
#             settings_data = response.text
#             settings_data = json.loads(settings_data)
#             settings_data_api = settings_data['data']

#             for k in settings_data_api:
#                 if k['option'] == "STOCK CE":
#                     set_CALL_pcr = k['set_pcr']
#                     profitPercentage_CALL = k['profit_percentage']
#                     lossPercentage_CALL = k['loss_percentage'] 
#                     lot_size_CALL = k['quantity_bn']

#             data = stock_for_buy.objects.filter(call_or_put='CALL').values()
#             stock_details = stock_detail.objects.values_list().values()
#             nseSetting = nse_setting.objects.values_list().values()
#             live_obj = live.objects.values_list().values()
#             live_call = live_obj[0]['live_stock_ce']

#             sorted_call = sorted(data, key=lambda i: -i['difference_ce_pe'])
#             stock_name = sorted_call[0]['stocks_name']

#             for k in nseSetting:
#                 if k['option'] == "STOCK CE":
#                     OptionId_CALL = k['id']
            
#             ## BUY Coondition
#             setBuyCondition_CALL = Coustom.buyCondition(stock_details, OptionId_CALL, "CALL")
               

#             baseurl = "https://www.nseindia.com/"
#             headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ''like Gecko) ''Chrome/80.0.3987.149 Safari/537.36','accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
#             session = requests.Session()
#             req = session.get(baseurl, headers=headers, timeout=5)
#             cookiess = dict(req.cookies)
#             stock_url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name
#             stock_response = requests.get(stock_url, headers=headers, cookies=cookiess, timeout=5).json()


#             livePrice = stock_response['records']['underlyingValue']
#             filteredData = stock_response['filtered']['data']

#             down_price = Coustom.downPrice(filteredData, livePrice)

#             up_price = Coustom.upPrice(filteredData, livePrice)
            
#             downSliceList = Coustom.downMaxValue(down_price[:-6:-1])

#             upSliceList = Coustom.upMaxValue(up_price[0:5])

#             PEMax, PEMaxValue = Coustom.basePriceData(down_price[:-6:-1], downSliceList)
            
#             CEMax, CEMaxValue = Coustom.resistancePriceData(up_price[0:5], upSliceList)

#             pcr = Coustom.pcrValue(stock_response)


#             for mx in PEMax:
#                 if setBuyCondition_CALL == True:
#                     diffrent_data =(up_price[0]['strikePrice'] + down_price[-1]['strikePrice'] ) / 2
#                     # diffrent_data = (diffrent_data + down_price[-1]['strikePrice']) / 2 
#                     # d_d = ((diffrent_data - down_price[-1]['strikePrice']) / 2) + down_price[-1]['strikePrice']
#                     # print(stock_name, livePrice,'<',diffrent_data,  livePrice <= diffrent_data)
#                     if livePrice <= down_price[-1]['strikePrice'] :
#                         strikePrice = mx['strikePrice']
#                         bdprice = mx['CE']['bidprice']
#                         sellPrice = '%.2f'% ((bdprice * profitPercentage_CALL) / 100 + bdprice)
#                         stop_loss = '%.2f'% (bdprice - (bdprice * lossPercentage_CALL ) / 100)
#                         squareoff_CE = '%.2f'% (( bdprice * profitPercentage_CALL ) / 100)
#                         stoploss_CE = '%.2f'% ((bdprice * lossPercentage_CALL ) / 100)
#                         postData = {'stock_name': stock_name, "buy_price": bdprice, "base_strike_price":strikePrice, "live_Strike_price":livePrice, "sell_price": sellPrice, "stop_loseprice": stop_loss, 'percentage': OptionId_CALL, 'call_put':'CALL'}
#                         stock_detail.objects.create(status="BUY",buy_price = bdprice, base_strike_price=strikePrice, live_Strike_price=livePrice, live_brid_price=bdprice, sell_price= sellPrice ,stop_loseprice=stop_loss, percentage_id=OptionId_CALL, stock_name = stock_name, call_put ='CALL', buy_pcr=pcr )
#                         # if live_call == True:
#                         #     sellFunStock(strikePrice, bdprice, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL, stock_name)
#                         consoleGreen.print('SuccessFully Buy Stock: ',postData)
#                     else:
#                         consoleYellow.print(stock_name,'->', livePrice , '<=', down_price[-1]['strikePrice'])




#             for sell in stock_details:
#                 if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_CALL and sell['call_put'] == 'CALL':
#                     if sell['stock_name'] != stock_name:
#                         stock_name = sell['stock_name']
#                         stock_url_sell = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name
#                         stock_response_sell = requests.get(stock_url_sell, headers=headers, timeout=5, cookies=cookiess).json()
#                         filteredData = stock_response_sell['filtered']['data']

#                     strikePrice_SELL = sell['base_strike_price']
#                     for filters in filteredData:
#                         if filters['strikePrice'] == strikePrice_SELL:
#                             buy_pricee = sell['buy_price'] 
#                             sell_Pricee = sell['sell_price']
#                             stop_Losss = sell['stop_loseprice']
#                             liveBidPrice_sell = filters['CE']['bidprice']
#                             stock_ID = sell['id']
#                             sell_time = timezone.now()

#                             if sell['admin_call'] == True and sell['status'] == 'BUY':
#                                 if buy_pricee < liveBidPrice_sell:
#                                     final_status_admin_call = 'PROFIT'
#                                 else:
#                                     final_status_admin_call = 'LOSS'
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_status_admin_call, exit_pcr= pcr )
#                                 consoleRed.print("SuccessFully SELL STOCK OF CALL")
#                                 # PcrUpdatee()
                                
#                             consoleBlue.print(stock_name, 'CALL---> ' ,'buy_pricee:', buy_pricee, 'sell_Pricee:', sell_Pricee, 'liveBidPrice:', liveBidPrice_sell, 'stop_Losss:', stop_Losss)
#                             if sell_Pricee <= liveBidPrice_sell :
#                                 final_statuss = "PROFIT"
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True, exit_pcr= pcr)
#                                 consoleBlue.print("SuccessFully SELL STOCK OF CALL")
#                             if stop_Losss > liveBidPrice_sell:
#                                 final_statuss = "LOSS"
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True, exit_pcr= pcr )
#                                 consoleBlue.print("SuccessFully SELL STOCK OF CALL")
#         except Exception as e:
#             consoleRed.print('Error-->', e)
#             consoleRed.print("Connection refused by the server...................................... STOCK CE")



# def StockPut():
#     PcrIsUpdating = extra_setting.objects.filter(id = 1).values()
#     if PcrIsUpdating[0]['pcr_isupdating'] == True :
#       consoleRed.print("Pcr is Updating Please Wait")
#     else:
#         try:
#             settings_url = 'https://zerodha.harmistechnology.com/setting_nse'
#             response = requests.get(settings_url)
#             settings_data = response.text
#             settings_data = json.loads(settings_data)
#             settings_data_api = settings_data['data']

#             for k in settings_data_api:
#                 if k['option'] == "STOCK PE":
#                     set_CALL_pcr = k['set_pcr']
#                     profitPercentage_CALL = k['profit_percentage']
#                     lossPercentage_CALL = k['loss_percentage'] 
#                     lot_size_PUT = k['quantity_bn']

#             data = stock_for_buy.objects.filter(call_or_put='PUT').values()
#             stock_details = stock_detail.objects.values_list().values()
#             nseSetting = nse_setting.objects.values_list().values()
#             live_obj = live.objects.values_list().values()
#             live_call = live_obj[0]['live_stock_pe']

#             sorted_call = sorted(data, key=lambda i: -i['difference_ce_pe'])
#             stock_name = sorted_call[0]['stocks_name']
            
#             for k in nseSetting:
#                 if k['option'] == "STOCK PE":
#                     OptionId_CALL = k['id']
                    
#             setBuyCondition_CALL = Coustom.buyCondition(stock_details, OptionId_CALL, "PUT")   

#             baseurl = "https://www.nseindia.com/"
#             headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, ''like Gecko) ''Chrome/80.0.3987.149 Safari/537.36','accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
#             session = requests.Session()
#             req = session.get(baseurl, headers=headers, timeout=5)
#             cookiess = dict(req.cookies)
#             stock_url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name
#             stock_response = requests.get(stock_url, headers=headers, cookies=cookiess, timeout=5).json()


#             livePrice = stock_response['records']['underlyingValue']
#             filteredData = stock_response['filtered']['data']

#             down_price = Coustom.downPrice(filteredData, livePrice)

#             up_price = Coustom.upPrice(filteredData, livePrice)
            
#             downSliceList = Coustom.downMaxValue(down_price[:-6:-1])

#             upSliceList = Coustom.upMaxValue(up_price[0:5])

#             PEMax, PEMaxValue = Coustom.basePriceData(down_price[:-6:-1], downSliceList)
            
#             CEMax, CEMaxValue = Coustom.resistancePriceData(up_price[0:5], upSliceList)

#             pcr = Coustom.pcrValue(stock_response)


#             for mx in CEMax:
#                 if setBuyCondition_CALL == True:
#                     diffrent_data =(up_price[0]['strikePrice'] + down_price[-1]['strikePrice'] ) / 2
#                     # diffrent_data = (diffrent_data + up_price[0]['strikePrice']) / 2 
#                     # d_d = ((diffrent_data - down_price[-1]['strikePrice']) / 2) + down_price[-1]['strikePrice']
#                     if livePrice >= up_price[0]['strikePrice'] :
#                         strikePrice = mx['strikePrice']
#                         bdprice = mx['PE']['bidprice']
#                         sellPrice = '%.2f'% ((bdprice * profitPercentage_CALL) / 100 + bdprice)
#                         stop_loss = '%.2f'% (bdprice - (bdprice * lossPercentage_CALL ) / 100)
#                         squareoff_PE = '%.2f'% (( bdprice * profitPercentage_CALL ) / 100)
#                         stoploss_PE = '%.2f'% ((bdprice * lossPercentage_CALL ) / 100)
#                         postData = {'stock_name': stock_name, "buy_price": bdprice, "base_strike_price":strikePrice, "live_Strike_price":livePrice, "sell_price": sellPrice, "stop_loseprice": stop_loss, 'percentage': OptionId_CALL, 'call_put':'PUT'}
#                         stock_detail.objects.create(status="BUY",buy_price = bdprice, base_strike_price=strikePrice, live_Strike_price=livePrice, live_brid_price=bdprice, sell_price= sellPrice ,stop_loseprice=stop_loss, percentage_id=OptionId_CALL, stock_name = stock_name, call_put ='PUT', buy_pcr=pcr )
#                         # if live_call == True:
#                         #     sellFunStock(strikePrice, bdprice, squareoff_PE, stoploss_PE, OptionId_CALL, lot_size_PUT, stock_name)

#                         consoleGreen.print('SuccessFully Buy Stock PUT: ',postData)
#                     else:
#                         consoleYellow.print(stock_name,'PUT ->', livePrice , '>=', up_price[0]['strikePrice'])




#             for sell in stock_details:
#                 if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_CALL and sell['call_put'] == 'PUT':
#                     if sell['stock_name'] != stock_name:
#                         stock_name = sell['stock_name']
#                         stock_url_sell = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name
#                         stock_response_sell = requests.get(stock_url_sell, headers=headers, timeout=5, cookies=cookiess).json()
#                         filteredData = stock_response_sell['filtered']['data']

#                     strikePrice_SELL = sell['base_strike_price']
#                     for filters in filteredData:
#                         if filters['strikePrice'] == strikePrice_SELL:
#                             buy_pricee = sell['buy_price'] 
#                             sell_Pricee = sell['sell_price']
#                             stop_Losss = sell['stop_loseprice']
#                             liveBidPrice_sell = filters['PE']['bidprice']
#                             stock_ID = sell['id']
#                             sell_time = timezone.now()

#                             if sell['admin_call'] == True and sell['status'] == 'BUY':
#                                 if buy_pricee < liveBidPrice_sell:
#                                     final_status_admin_call = 'PROFIT'
#                                 else:
#                                     final_status_admin_call = 'LOSS'
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_status_admin_call, exit_pcr= pcr )
#                                 consoleBlue.print("SuccessFully SELL STOCK OF PUT")
#                                 # PcrUpdatee()

#                             consoleBlue.print(stock_name, 'PUT---> ' ,'buy_pricee:', buy_pricee, 'sell_Pricee:', sell_Pricee, 'liveBidPrice:', liveBidPrice_sell, 'stop_Losss:', stop_Losss)
#                             if sell_Pricee <= liveBidPrice_sell :
#                                 final_statuss = "PROFIT"
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True, exit_pcr= pcr)
#                                 consoleBlue.print("SuccessFully SELL STOCK OF PUT")
#                             if stop_Losss > liveBidPrice_sell:
#                                 final_statuss = "LOSS"
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True, exit_pcr= pcr )
#                                 consoleBlue.print("SuccessFully SELL STOCK OF PUT")
#         except Exception as e:
#             consoleRed.print('Error-->', e)
#             consoleRed.print("Connection refused by the server...................................... STOCK PE")



# def Stock():
#     try:
#         url = 'https://zerodha.harmistechnology.com/selectname'
#         response = requests.get(url).json()
#         stock_name = response['data'][0]['name']
#         # stock_name = ''
#         if stock_name == 'NO DATA':
#             pass
#             # consoleYellow.print('Please Select Stock in CALL')
#         else:
#             baseurl = "https://www.nseindia.com/"
#             headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
#                                 'like Gecko) '
#                                 'Chrome/80.0.3987.149 Safari/537.36',
#                 'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
#             session = requests.Session()
#             req = session.get(baseurl, headers=headers, timeout=5)
#             cookiess = dict(req.cookies)
#             stock_url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name

#             stock_response = requests.get(stock_url, headers=headers, cookies=cookiess, timeout=5).json()

#             # time_stamp = stock_response['records']['timestamp']
#             livePrice = stock_response['records']['underlyingValue']
#             filteredData = stock_response['filtered']['data']
#             summ = stock_response['filtered']['CE']['totOI']
#             summ2 = stock_response['filtered']['PE']['totOI']
#             stock_pcr = '%.2f'% (summ2 / summ)

#             up_price = []
#             up__price = stock_response['filtered']['data']
#             for up in up__price:
#                 if up['strikePrice'] >= livePrice:
#                     up_price.append(up) 

#             upside_first = up_price[0]

#             down_price = []
#             down__price = stock_response['filtered']['data']
#             for down in down__price:
#                 if down['strikePrice'] <= livePrice:
#                     down_price.append(down)
#             downside_first = down_price[-1]

#             # downside_first_Diff = []
#             # for down_first in downside_first:
#             #     down_first_PE = down_first['PE']['openInterest'] + down_first['PE']['changeinOpenInterest']
#             #     down_first_CE = down_first['CE']['openInterest'] + down_first['CE']['changeinOpenInterest']
#             #     downside_first_Diff.append(down_first_PE - down_first_CE)
            
#             stock_details = stock_detail.objects.values_list().values()
#             nseSetting = nse_setting.objects.values_list().values()

#             for k in nseSetting:
#                 if k['option'] == "STOCK CE":
#                     OptionId_CALL = k['id']

#             settings_url = 'https://zerodha.harmistechnology.com/setting_nse'
#             response = requests.get(settings_url)
#             settings_data = response.text
#             settings_data = json.loads(settings_data)
#             settings_data_api = settings_data['data']

#             for k in settings_data_api:
#                 if k['option'] == "STOCK CE":
#                     set_CALL_pcr = k['set_pcr']
#                     profitPercentage_CALL = k['profit_percentage']
#                     lossPercentage_CALL = k['loss_percentage']    

#             if stock_details.exists():
#                 # print('------------------------------------- STOCK --------------------------------------------')
#                 pass
#             else:
#                 now = datetime.now()
#                 yesterday = now - timedelta(days = 1)
#                 stock_details = [{'percentage_id':0, "status": '', "call_put":"",'buy_time':yesterday }]

#             for i in stock_details:
#                 if i['percentage_id'] == OptionId_CALL and i['status'] == 'BUY' and i['call_put'] == "CALL" :
#                     setBuyCondition_CALL = False
#                     break
#                 else:
#                     setBuyCondition_CALL = True


#             if setBuyCondition_CALL == True :
#                 if set_CALL_pcr < float(stock_pcr):
#                     diffrent_data =( upside_first['strikePrice'] + downside_first['strikePrice'] ) / 2
#                     d_d = ((diffrent_data - downside_first['strikePrice']) / 2) + downside_first['strikePrice']
#                     if d_d <= livePrice and livePrice <= diffrent_data :
#                         strikePrice = downside_first['strikePrice']
#                         bdprice = downside_first['CE']['bidprice']
#                         sellPrice = '%.2f'% ((bdprice * profitPercentage_CALL) / 100 + bdprice)
#                         stop_loss = '%.2f'% (bdprice - (bdprice * lossPercentage_CALL ) / 100)

#                         postData = {'stock_name': stock_name, "buy_price": bdprice, "base_strike_price":strikePrice, "live_Strike_price":livePrice, "sell_price": sellPrice, "stop_loseprice": stop_loss, 'percentage': OptionId_CALL, 'call_put':'CALL'}
#                         stock_detail.objects.create(status="BUY",buy_price = bdprice, base_strike_price=strikePrice, live_Strike_price=livePrice, live_brid_price=bdprice, sell_price= sellPrice ,stop_loseprice=stop_loss, percentage_id=OptionId_CALL, stock_name = stock_name, call_put ='CALL', buy_pcr=stock_pcr )
#                         print('SuccessFully Buy Stock: ',postData)
#                     else:
#                         print(stock_name,'->',d_d, livePrice, diffrent_data)
#                 else:
#                     print('YOU CAN BUY STOCK OF', stock_name)
#             else:
#                 print("CANI'T BUY YOU HAVE A STOCK")


#             for sell in stock_details:
#                 if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_CALL and sell['call_put'] == 'CALL':
#                     if sell['stock_name'] != stock_name:
#                         stock_name = sell['stock_name']
#                         stock_url_sell = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name
#                         stock_response_sell = requests.get(stock_url_sell, headers=headers, timeout=5, cookies=cookiess).json()
#                         filteredData = stock_response_sell['filtered']['data']

#                     strikePrice_SELL = sell['base_strike_price']
#                     for filters in filteredData:
#                         if filters['strikePrice'] == strikePrice_SELL:
#                             buy_pricee = sell['buy_price'] 
#                             sell_Pricee = sell['sell_price']
#                             stop_Losss = sell['stop_loseprice']
#                             liveBidPrice_sell = filters['CE']['bidprice']
#                             stock_ID = sell['id']
#                             sell_time = timezone.now()

#                             if sell['admin_call'] == True and sell['status'] == 'BUY':
#                                 if buy_pricee < liveBidPrice_sell:
#                                     final_status_admin_call = 'PROFIT'
#                                 else:
#                                     final_status_admin_call = 'LOSS'
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_status_admin_call, exit_pcr= stock_pcr )
#                                 print("SuccessFully SELL STOCK OF CALL")
                    
#                             print(stock_name, 'CALL---> ' ,'buy_pricee:', buy_pricee, 'sell_Pricee:', sell_Pricee, 'liveBidPrice:', liveBidPrice_sell, 'stop_Losss:', stop_Losss)
#                             if sell_Pricee <= liveBidPrice_sell :
#                                 final_statuss = "PROFIT"
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True, exit_pcr= stock_pcr)
#                                 print("SuccessFully SELL STOCK OF CALL")
#                             if stop_Losss > liveBidPrice_sell:
#                                 final_statuss = "LOSS"
#                                 stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True, exit_pcr= stock_pcr )
#                                 print("SuccessFully SELL STOCK OF CALL")
#     except Exception as e:
#         print('Error-->', e)
#         print("Connection refused by the server........................................ STOCK")

