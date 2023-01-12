from nse_app.models import *
from django.utils import timezone
import datetime
import requests
import json
import pprint
from datetime import date, datetime, timedelta
from django.utils.dateformat import DateFormat
from django.shortcuts import render
import pyotp
from smartapi import SmartConnect
import pandas as pd


def sellFun(strikePrice, BidPrice, squareoff, stoploss, OptionId, lots):
    # print("DATAAAAA--------->", strikePrice, BidPrice, squareoff, stoploss, OptionId)
    base_strike_price_sm = float(strikePrice)
    buy_price_sm = str(BidPrice)
    squareoff_sm = squareoff
    stoploss_sm = stoploss
    percentions_sm = OptionId
    lot_size = lots

    username = 'H117838'
    apikey = 'SqtdCpAg'
    pwd = '4689'
    totp = pyotp.TOTP("K7QDKSEXWD7KRO7EVQCUHTFK2U").now()
    obj = SmartConnect(api_key=apikey)
    dataa = obj.generateSession(username, pwd, totp)

    # refreshToken= data['data']['refreshToken']
    # feedToken=obj.getfeedToken()
    # userProfile= obj.getProfile(refreshToken)
    # print(userProfile)

    def place_order(token, symbol, qty, buy_sell, ordertype, price, variety='ROBO', exch_seg='NFO', triggerprice=stoploss_sm):
        total_qty = float(qty) * lot_size
        total_qty = int(total_qty)
        total_qty = str(total_qty)
        try:
            orderparams = {
                "variety": 'ROBO',
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": 'BUY',
                'exchange': 'NFO',
                "ordertype": 'LIMIT',
                "producttype": 'BO',
                "duration": "DAY",
                "price": buy_price_sm,
                "squareoff": squareoff_sm,
                "stoploss": stoploss_sm,
                "quantity": total_qty,
                "trailingStopLoss": "5",
            }
            print(orderparams)
            orderId = obj.placeOrder(orderparams)
            print("The order id is: {}".format(orderId))

        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))

    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(
        token_df['expiry']).apply(lambda x: x.date())
    token_df = token_df.astype({'strike': float})

    def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):
        df = token_df
        strike_price = strike_price*100
        if exch_seg == 'NSE':
            eq_df = df[(df['exch_seg'] == 'NSE')]
            return eq_df[eq_df['name'] == symbol]
        elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
            return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
        elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
            return df[(df['exch_seg'] == 'NFO') & (df['expiry'] == expiry_day) & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])

    a = date(2023, 1, 19)

    if percentions_sm == 3:
        symbol = 'BANKNIFTY'
        pe_strike_symbol = getTokenInfo(
            symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', a).iloc[0]
        place_order(pe_strike_symbol['token'], pe_strike_symbol['symbol'],
                    pe_strike_symbol['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')
        # print("BANKNIFTY pe", pe_strike_symbol)

    elif percentions_sm == 1:
        symbol = 'BANKNIFTY'

        ce_strike_symbol = getTokenInfo(
            symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', a).iloc[0]
        place_order(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')
        # print("BANKNIFTY ce", ce_strike_symbol)

    elif percentions_sm == 4:
        symbol = 'NIFTY'
        qty = 25
        pe_strike_symbol = getTokenInfo(
            symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', a).iloc[0]
        place_order(pe_strike_symbol['token'], pe_strike_symbol['symbol'],
                    pe_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO', qty)
        # print("NIFTY pe", pe_strike_symbol)

    elif percentions_sm == 2:
        symbol = 'NIFTY'
        ce_strike_symbol = getTokenInfo(
            symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', a).iloc[0]
        place_order(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')





def NIFTY():
    try:
        baseurl = "https://www.nseindia.com/"
        headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
        session = requests.Session()
        req = session.get(baseurl, headers=headers, timeout=5)
        cookies = dict(req.cookies)

        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        
        response = requests.get(url, headers=headers,
        #  timeout=5, cookies=cookies
        )
        data = response.text
        api_data = json.loads(data)
        # -------------------------------------  API DATA   ---------------------------------------------------------
        timestamp = api_data['records']['timestamp']
        livePrice = api_data['records']['underlyingValue']
        f_data = api_data['filtered']['data']

        filteredData = api_data['filtered']['data']
        down_price = []
        down__price = api_data['filtered']['data']
        for down in down__price:
            if down['strikePrice'] <= livePrice:
                down_price.append(down) 

        up_price = []
        up__price = api_data['filtered']['data']
        for up in up__price:
            if up['strikePrice'] >= livePrice:
                up_price.append(up) 

        downSliceList = []
        for downSlice in down_price[:-6:-1]:
            ss = downSlice['PE']['openInterest'] + downSlice['PE']['changeinOpenInterest']
            downSliceList.append(ss)
        downSliceList.sort()
        downSliceList.reverse()
        downSliceList = downSliceList[:1]

        upSliceList = []
        for upSlice in up_price[0:5]:
            ss = upSlice['CE']['openInterest'] + upSlice['CE']['changeinOpenInterest']
            upSliceList.append(ss)
        upSliceList.sort()
        upSliceList.reverse()
        upSliceList = upSliceList[:1]

        PEMax = []
        PEMaxValue = []
        for downn in down_price:
            aaa = downn['PE']['changeinOpenInterest'] + downn['PE']['openInterest']
            if aaa == downSliceList[0]:
                PEMax.append(downn)
                PEMaxValue.append(downn['strikePrice'])

        CEMax = []
        CEMaxValue = []
        for upp in up_price:
            upppp = upp['CE']['changeinOpenInterest'] + upp['CE']['openInterest']
            if upppp == upSliceList[0]:
                CEMax.append(upp)
                CEMaxValue.append(upp['strikePrice'])
                
        summ = api_data['filtered']['CE']['totOI']
        summ2 = api_data['filtered']['PE']['totOI']
        pcr = summ2 / summ
        # print(pcr)

        for pe in PEMax:
            cepeDiffrent = pe['PE']['openInterest'] + pe['PE']['changeinOpenInterest'] - (pe['CE']['openInterest'] + pe['CE']['changeinOpenInterest'])
        cepeDiffrent = (cepeDiffrent)

        # --------------------------------------------------------------------------------------------------------------------------------------

        stock_details = stock_detail.objects.values_list().values()
        nseSetting = nse_setting.objects.values_list().values()
        live_obj = live.objects.values_list().values()
        live_call = live_obj[0]['live_set']

        settings_url = 'https://zerodha.harmistechnology.com/setting_nse'
        response = requests.get(settings_url)
        settings_data = response.text
        settings_data = json.loads(settings_data)
        settings_data_api = settings_data['data']
        
        for k in settings_data_api:
            if k['option'] == "NIFTY CE":
                set_CALL_pcr = k['set_pcr']
                basePlus_CALL = k['baseprice_plus']
                profitPercentage_CALL = k['profit_percentage']
                lossPercentage_CALL = k['loss_percentage']
                lot_size_CALL = k['quantity_bn']
            if k['option'] == "NIFTY PE":
                set_PUT_pcr = k['set_pcr']
                basePlus_PUT = k['baseprice_plus']
                profitPercentage_PUT = k['profit_percentage']
                lossPercentage_PUT = k['loss_percentage']
                lot_size_PUT = k['quantity_bn'] 
                
        for k in nseSetting:
            if k['option'] == "NIFTY CE":
                OptionId_CALL = k['id']
                # set_CALL_pcr = k['set_pcr']
                # basePlus_CALL = k['baseprice_plus']
                # profitPercentage_CALL = k['profit_percentage']
                # lossPercentage_CALL = k['loss_percentage']
            if k['option'] == "NIFTY PE":
                OptionId_PUT = k['id']
                # set_PUT_pcr = k['set_pcr']
                # basePlus_PUT = k['baseprice_plus']
                # profitPercentage_PUT = k['profit_percentage']
                # lossPercentage_PUT = k['loss_percentage']

            # ---------------------- CE BUY CONDITION ----------------------------------
        if stock_details.exists():
            # print('------------------------------------- NIFTY --------------------------------------------')
            pass
        else:
            now = datetime.now()
            yesterday = now - timedelta(days = 1)
            stock_details = [{'percentage_id':0, "status": '', "call_put":"",'buy_time':yesterday }]
        profit_CE = 0
        loss_CE = 0
        for i in stock_details:
            if i['percentage_id'] == 2 and i['status'] == 'BUY' and i['call_put'] == "CALL" :
                setBuyCondition_CALL = False
                break
            else:
                setBuyCondition_CALL = True

            buy_time_call = i['buy_time']
            buyy_date_call = datetime.date(buy_time_call)
            today = date.today()

            if buyy_date_call == today and i['percentage_id'] == 2:
                if i['final_status'] == "PROFIT":
                    profit_CE = profit_CE + 1
                elif i['final_status'] == "LOSS":
                    loss_CE = loss_CE + 1
        if profit_CE > loss_CE:
            setOneStock_CALL = False
            print("YOU MAKE PROFIT TODAY IN NIFTY CALL")
        else:
            setOneStock_CALL = True
            # ---------------------- PE BUY CONDITION
        profit_PUT = 0
        loss_PUT = 0
        for j in stock_details:
            if j['percentage_id'] == 4 and j['status'] == 'BUY' and j['call_put'] == "PUT" :
                setBuyCondition_PUT = False
                break
            else:
                setBuyCondition_PUT = True

            buy_time_PUT = j['buy_time']
            buyy_date_PUT = datetime.date(buy_time_PUT)

            today = date.today()
            if buyy_date_PUT == today and j['percentage_id'] == 4:
                if j['final_status'] == "PROFIT":
                    profit_PUT = profit_PUT + 1
                elif j['final_status'] == "LOSS":
                    loss_PUT = loss_PUT + 1
        if profit_PUT > loss_PUT:
            setOneStock_PUT = False
            print("YOU MAKE PROFIT TODAY IN NIFTY PUT")
        else:
            setOneStock_PUT = True

        # pprint.pprint(PEMax)
        for mx in PEMax:
            if PEMaxValue != CEMaxValue and cepeDiffrent >= 50000:
                
                if setOneStock_CALL == True:
                    if setBuyCondition_CALL == True:
                        if pcr >= set_CALL_pcr:
                            call_call = "CALL"
                            basePricePlus_CALL = mx['strikePrice'] + basePlus_CALL
                            basePricePlus_CALL_a = basePricePlus_CALL - 15
                            print('----------------------------------> NIFTY CE:',basePricePlus_CALL_a, livePrice, basePricePlus_CALL)
                            if basePricePlus_CALL_a <= livePrice and livePrice <= basePricePlus_CALL:
                                BidPrice_CE = mx['CE']['bidprice']
                                squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                                stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                                sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                                stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                                strikePrice_CE = mx['strikePrice']
                                # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put =call_call, buy_pcr = '%.5f'% (pcr) )
                                postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put':call_call}
                                if live_call == True:
                                    sellFun(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL)
                                print('SuccessFully Buy IN NIFTY CALL: ',postData)
                        else:
                            print('YOU CAN BUY STOCK IN NIFTY CALL: ')
                    else:
                        print("CAN'T BUY YOU HAVE STOCK OF NIFTY CALL")

                if setOneStock_PUT == True:
                    if setBuyCondition_PUT == True:
                        if pcr <= set_PUT_pcr:
                            put_put = "PUT"
                            basePricePlus_PUT = mx['strikePrice'] + basePlus_PUT
                            basePricePlus_PUT_a = basePricePlus_PUT - 15
                            # if livePrice <= basePricePlus_PUT:
                            print('----------------------------------> NIFTY PE:',basePricePlus_PUT_a, livePrice, basePricePlus_PUT)
                            if basePricePlus_PUT_a <= livePrice and livePrice <= basePricePlus_PUT:
                                BidPrice_PUT = mx['PE']['bidprice']
                                squareoff_PUT = '%.2f'% (( BidPrice_PUT * profitPercentage_PUT ) / 100)
                                stoploss_PUT = '%.2f'% ((BidPrice_PUT * lossPercentage_PUT ) / 100)
                                sellPrice_PUT = '%.2f'% ((BidPrice_PUT * profitPercentage_PUT) / 100 + BidPrice_PUT)
                                stop_loss_PUT = '%.2f'% (BidPrice_PUT - (BidPrice_PUT * lossPercentage_PUT ) / 100)
                                strikePrice_PUT = mx['strikePrice']
                                # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_PUT,live_brid_price=BidPrice_PUT , base_strike_price=strikePrice_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PUT ,stop_loseprice=stop_loss_PUT, percentage_id=OptionId_PUT , call_put =put_put, buy_pcr = '%.5f'% (pcr) )
                                postData = { "buy_price": BidPrice_PUT, "base_strike_price":strikePrice_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PUT, "stop_loseprice": stop_loss_PUT, 'percentage': OptionId_PUT, 'call_put':put_put}
                                if live_call == True:
                                    sellFun(strikePrice_PUT, BidPrice_PUT, squareoff_PUT, stoploss_PUT, OptionId_PUT, lot_size_PUT)
                                print('SuccessFully Buy IN NIFTY PUT: ',postData)
                        else:
                            print('YOU CAN BUY STOCK IN NIFTY PUT: ')
                    else:
                        print("CAN'T BUY YOU HAVE STOCK OF NIFTY PUT")

        
        for sell in stock_details:
            
            if sell['status'] == 'BUY' and sell['percentage_id'] == 2 and sell['call_put'] == 'CALL':
                strikePrice_SELL = sell['base_strike_price']
                for filters in filteredData:
                    if filters['strikePrice'] == strikePrice_SELL:
                        buy_pricee = sell['buy_price'] 
                        sell_Pricee = sell['sell_price']
                        stop_Losss = sell['stop_loseprice']
                        liveBidPrice = filters['CE']['bidprice']
                        stock_ID = sell['id']
                        sell_time = timezone.now()
                        
                        if sell['admin_call'] == True and sell['status'] == 'BUY':
                            if buy_pricee < liveBidPrice:
                                final_status_admin_call = 'PROFIT'
                            else:
                                final_status_admin_call = 'LOSS'
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status_admin_call, exit_pcr= '%.5f'% (pcr))
                            print("SuccessFully SELL STOCK OF CALL")
                
                        print('NIFTY CALL-> ' ,'buy_pricee: ', buy_pricee, 'sell_Pricee: ', sell_Pricee, 'liveBidPrice: ', liveBidPrice, 'stop_Losss: ', stop_Losss)
                        if sell_Pricee <= liveBidPrice :
                            final_statuss = "PROFIT"
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True, exit_pcr= '%.5f'% (pcr))
                            print("SuccessFully SELL STOCK OF CALL")
                        if stop_Losss >= liveBidPrice:
                            final_statuss = "LOSS"
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True, exit_pcr= '%.5f'% (pcr) )
                            print("SuccessFully SELL STOCK OF CALL")
                        # pprint.pprint(stock_ID)
            
            if sell['status'] == 'BUY' and sell['percentage_id'] == 4 and sell['call_put'] == 'PUT':
                strikePrice_SELL_PUT = sell['base_strike_price']
                for filters_put in filteredData:
                    if filters_put['strikePrice'] == strikePrice_SELL_PUT:
                        buy_pricee_put = sell['buy_price'] 
                        sell_Pricee_put = sell['sell_price']
                        stop_Losss_put = sell['stop_loseprice']
                        liveBidPrice_put = filters_put['PE']['bidprice']
                        stock_ID_put = sell['id']
                        sell_time_put = timezone.now()
                        
                        if sell['admin_call'] == True and sell['status'] == 'BUY':
                            if buy_pricee_put < liveBidPrice_put:
                                final_status_admin_PUT = 'PROFIT'
                            else:
                                final_status_admin_PUT = 'LOSS'
                            print("SuccessFully SELL STOCK OF PUT")
                            stock_detail.objects.filter(id=stock_ID_put).update(status = 'SELL', exit_price = liveBidPrice_put, sell_buy_time=sell_time_put, final_status = final_status_admin_PUT, exit_pcr= '%.5f'% (pcr))        
                            
                        print('NIFTY PUT-> ' ,'buy_pricee: ', buy_pricee_put, 'sell_Pricee: ', sell_Pricee_put, 'liveBidPrice: ', liveBidPrice_put, 'stop_Losss: ', stop_Losss_put)
                        if sell_Pricee_put <= liveBidPrice_put :
                            final_statuss_put = "PROFIT"
                            stock_detail.objects.filter(id=stock_ID_put).update(status = 'SELL', exit_price = liveBidPrice_put, sell_buy_time=sell_time_put, final_status = final_statuss_put, admin_call = True, exit_pcr= '%.5f'% (pcr))        
                            print("SuccessFully SELL STOCK OF PUT")
                        if stop_Losss_put >= liveBidPrice_put:
                            final_statuss_put = "LOSS"
                            stock_detail.objects.filter(id=stock_ID_put).update(status = 'SELL', exit_price = liveBidPrice_put, sell_buy_time=sell_time_put, final_status = final_statuss_put, admin_call = True, exit_pcr= '%.5f'% (pcr))        
                            print("SuccessFully SELL STOCK OF PUT")
    except:
                print("Connection refused by the server...................................... NIFTY")






# import random

# def print_hello():
#     number = random.randint(0, 100)
#     # Category.objects.create(category_name= number)