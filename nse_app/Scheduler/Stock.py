from nse_app.models import *
import requests
import json
from datetime import datetime, timedelta
from django.utils import timezone



def Stock():
    try:
        url = 'https://zerodha.harmistechnology.com/selectname'
        response = requests.get(url).json()
        stock_name = response['data'][0]['name']

        
        baseurl = "https://www.nseindia.com/"
        headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
        session = requests.Session()
        req = session.get(baseurl, headers=headers, timeout=5)
        cookiess = dict(req.cookies)
        stock_url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name

        stock_response = requests.get(stock_url, headers=headers, cookies=cookiess, timeout=5).json()

        # time_stamp = stock_response['records']['timestamp']
        livePrice = stock_response['records']['underlyingValue']
        filteredData = stock_response['filtered']['data']
        summ = stock_response['filtered']['CE']['totOI']
        summ2 = stock_response['filtered']['PE']['totOI']
        stock_pcr = '%.2f'% (summ2 / summ)

        up_price = []
        up__price = stock_response['filtered']['data']
        for up in up__price:
            if up['strikePrice'] >= livePrice:
                up_price.append(up) 

        upside_first = up_price[0]

        down_price = []
        down__price = stock_response['filtered']['data']
        for down in down__price:
            if down['strikePrice'] <= livePrice:
                down_price.append(down)
        downside_first = down_price[-1]

        # downside_first_Diff = []
        # for down_first in downside_first:
        #     down_first_PE = down_first['PE']['openInterest'] + down_first['PE']['changeinOpenInterest']
        #     down_first_CE = down_first['CE']['openInterest'] + down_first['CE']['changeinOpenInterest']
        #     downside_first_Diff.append(down_first_PE - down_first_CE)
        
        stock_details = stock_detail.objects.values_list().values()
        nseSetting = nse_setting.objects.values_list().values()

        for k in nseSetting:
            if k['option'] == "STOCK CE":
                OptionId_CALL = k['id']

        settings_url = 'https://zerodha.harmistechnology.com/setting_nse'
        response = requests.get(settings_url)
        settings_data = response.text
        settings_data = json.loads(settings_data)
        settings_data_api = settings_data['data']

        for k in settings_data_api:
            if k['option'] == "STOCK CE":
                set_CALL_pcr = k['set_pcr']
                profitPercentage_CALL = k['profit_percentage']
                lossPercentage_CALL = k['loss_percentage']    

        if stock_details.exists():
            # print('------------------------------------- STOCK --------------------------------------------')
            pass
        else:
            now = datetime.now()
            yesterday = now - timedelta(days = 1)
            stock_details = [{'percentage_id':0, "status": '', "call_put":"",'buy_time':yesterday }]

        for i in stock_details:
            if i['percentage_id'] == 5 and i['status'] == 'BUY' and i['call_put'] == "CALL" :
                setBuyCondition_CALL = False
                break
            else:
                setBuyCondition_CALL = True


        if setBuyCondition_CALL == True :
            if set_CALL_pcr < float(stock_pcr):
                diffrent_data =( upside_first['strikePrice'] + downside_first['strikePrice'] ) / 2
                d_d = ((diffrent_data - downside_first['strikePrice']) / 2) + downside_first['strikePrice']
                if d_d <= livePrice and livePrice <= diffrent_data :
                    strikePrice = downside_first['strikePrice']
                    bdprice = downside_first['CE']['bidprice']
                    sellPrice = '%.2f'% ((bdprice * profitPercentage_CALL) / 100 + bdprice)
                    stop_loss = '%.2f'% (bdprice - (bdprice * lossPercentage_CALL ) / 100)

                    postData = {'stock_name': stock_name, "buy_price": bdprice, "base_strike_price":strikePrice, "live_Strike_price":livePrice, "sell_price": sellPrice, "stop_loseprice": stop_loss, 'percentage': OptionId_CALL, 'call_put':'CALL'}
                    stock_detail.objects.create(status="BUY",buy_price = bdprice, base_strike_price=strikePrice, live_Strike_price=livePrice, live_brid_price=bdprice, sell_price= sellPrice ,stop_loseprice=stop_loss, percentage_id=OptionId_CALL, stock_name = stock_name, call_put ='CALL' )
                    print('SuccessFully Buy Stock: ',postData)
                else:
                    print(stock_name,'->',d_d, livePrice, diffrent_data)
            else:
                print('YOU CAN BUY STOCK OF', stock_name)
        else:
            print("CANI'T BUY YOU HAVE A STOCK")


        for sell in stock_details:
            if sell['status'] == 'BUY' and sell['percentage_id'] == 5 and sell['call_put'] == 'CALL':
                if sell['stock_name'] != stock_name:
                    stock_name = sell['stock_name']
                    stock_url_sell = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock_name
                    stock_response_sell = requests.get(stock_url_sell, headers=headers, timeout=5, cookies=cookiess).json()
                    filteredData = stock_response_sell['filtered']['data']

                strikePrice_SELL = sell['base_strike_price']
                for filters in filteredData:
                    if filters['strikePrice'] == strikePrice_SELL:
                        buy_pricee = sell['buy_price'] 
                        sell_Pricee = sell['sell_price']
                        stop_Losss = sell['stop_loseprice']
                        liveBidPrice_sell = filters['CE']['bidprice']
                        stock_ID = sell['id']
                        sell_time = timezone.now()

                        if sell['admin_call'] == True and sell['status'] == 'BUY':
                            if buy_pricee < liveBidPrice_sell:
                                final_status_admin_call = 'PROFIT'
                            else:
                                final_status_admin_call = 'LOSS'
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_status_admin_call)
                            print("SuccessFully SELL STOCK OF CALL")
                
                        print(stock_name, 'CALL---> ' ,'buy_pricee:', buy_pricee, 'sell_Pricee:', sell_Pricee, 'liveBidPrice:', liveBidPrice_sell, 'stop_Losss:', stop_Losss)
                        if sell_Pricee <= liveBidPrice_sell :
                            final_statuss = "PROFIT"
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True)
                            print("SuccessFully SELL STOCK OF CALL")
                        if stop_Losss > liveBidPrice_sell:
                            final_statuss = "LOSS"
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice_sell, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True )
                            print("SuccessFully SELL STOCK OF CALL")
    except:
        print("Connection refused by the server....... STOCK")
