from nse_app.models import *
from django.utils import timezone
import datetime
import requests
import json
from datetime import date, datetime, timedelta
import pyotp
from smartapi import SmartConnect
import pandas as pd




def sellFun(strikePrice, BidPrice, squareoff, stoploss, OptionId, lots):
   
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
    # data
    # refreshToken= data['data']['refreshToken']
    # feedToken=obj.getfeedToken()
    # userProfile= obj.getProfile(refreshToken)
    # print(userProfile)
    def place_order_pcr(token, symbol, qty,exch_seg ,buy_sell,ordertype ,price, variety='ROBO', triggerprice=5):
        total_qty = float(qty) * lot_size
        total_qty = int(total_qty)
        total_qty = str(total_qty)
        try:
            orderparams = {
                "variety": 'NORMAL',
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": 'BUY',
                'exchange': 'NFO',
                "ordertype": 'LIMIT',
                "producttype": 'CARRYFORWARD',
                "duration": "DAY",
                "price": buy_price_sm,    
                "squareoff": '0',
                "stoploss": '0',
                "quantity":total_qty,
            }
            print(orderparams)
            orderId = obj.placeOrder(orderparams)
            print("The order id is: {}".format(orderId))
            # stock_detail.objects.filter(id = get_id).update(orderid = orderId)
        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))                   

    def place_order(token, symbol, qty, buy_sell, ordertype, price, variety='ROBO', exch_seg='NFO', triggerprice=5):
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

    a = date(2023, 3, 9)

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

    ## place_order_pcr
    elif percentions_sm == 6:
        symbol = 'BANKNIFTY'
        ce_strike_symbol = getTokenInfo(
            symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', a).iloc[0]
        place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

    elif percentions_sm == 9:
        symbol = 'BANKNIFTY'
        ce_strike_symbol = getTokenInfo(
            symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', a).iloc[0]
        place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')



def BANKNIFTY():
    try:
        headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

        url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

        response = requests.get(url, headers=headers)
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

        cepeDiffrent = cepeDiffrent

        ## SETTINGS 
        stock_details = stock_detail.objects.values_list().values()
        nseSetting = nse_setting.objects.values_list().values()
        live_obj = live.objects.values_list().values()
        live_call = live_obj[0]['live_banknifty']
        pcr_options = pcr_option.objects.values_list().values()
        
        for pcrobj in pcr_options:
            if pcrobj['OptionName'] == 'BankNiftyPcrCALL':
                PcrObj_Call_ID = pcrobj['id']
                banknifty_pcr_stoploss_CALL = pcrobj['PcrStopLoss']
                banknifty_at_set_pcr_CALL = pcrobj['AtSetPcr']
                banknifty_live_pcr = pcrobj['LivePcr']
            if pcrobj['OptionName'] == 'BankNiftyPcrPUT':
                PcrObj_Put_ID = pcrobj['id']
                banknifty_pcr_stoploss_PUT = pcrobj['PcrStopLoss']
                banknifty_at_set_pcr_PUT = pcrobj['AtSetPcr']
                banknifty_live_pcr = pcrobj['LivePcr']
            
        ## API SETTINGS
        settings_url = 'https://zerodha.harmistechnology.com/setting_nse'
        response = requests.get(settings_url)
        settings_data = response.text
        settings_data = json.loads(settings_data)
        settings_data_api = settings_data['data']
        
        for k in settings_data_api:
            if k['option'] == "BANKNIFTY CE":
                set_CALL_pcr = k['set_pcr']
                basePlus_CALL = k['baseprice_plus']
                profitPercentage_CALL = k['profit_percentage']
                lossPercentage_CALL = k['loss_percentage']
                lot_size_CALL = k['quantity_bn']
            if k['option'] == "BANKNIFTY PE":
                set_PUT_pcr = k['set_pcr']
                basePlus_PUT = k['baseprice_plus']
                profitPercentage_PUT = k['profit_percentage']
                lossPercentage_PUT = k['loss_percentage']
                lot_size_PUT = k['quantity_bn'] 
            if k['option'] == 'BANKNIFTY_BASE_CE':
                set_call_pcr = k['set_pcr']
                lot_size_pcr_call = k['quantity_bn']
            if k['option'] == 'BANKNIFTY_PCR_PE':
                set_put_pcr = k['set_pcr']
                lot_size_pcr_put = k['quantity_bn']
                
        for k in nseSetting:
            if k['option'] == "BANKNIFTY CE":
                OptionId_CALL = k['id']
            if k['option'] == "BANKNIFTY PE":
                OptionId_PUT = k['id']
            if k['option'] == "BANKNIFTY_BASE_CE":
                OptionId_PCR_CALL = k['id']
            if k['option'] == "BANKNIFTY_PCR_PE":
                OptionId_PCR_PUT = k['id']        
            
        if stock_details.exists():
            pass
        else:
            now = datetime.now()
            yesterday = now - timedelta(days = 1)
            stock_details = [{'percentage_id':0, "status": '', "call_put":"",'buy_time':yesterday }]

        ## CALL
        profit_CE = 0
        loss_CE = 0
        for i in stock_details:
            if i['percentage_id'] == OptionId_CALL and i['status'] == 'BUY' and i['call_put'] == "CALL" :
                setBuyCondition_CALL = False
                break
            else:
                setBuyCondition_CALL = True

            buy_time_call = i['buy_time']
            buyy_date_call = datetime.date(buy_time_call)
            today = date.today()

            if buyy_date_call == today and i['percentage_id'] == 1:
                if i['final_status'] == "PROFIT":
                    profit_CE = profit_CE + 1
                elif i['final_status'] == "LOSS":
                    loss_CE = loss_CE + 1
        if profit_CE > loss_CE:
            setOneStock_CALL = False
            print("YOU MAKE PROFIT TODAY IN BANKNIFTY CALL")
        else:
            setOneStock_CALL = True

        ## PUT
        profit_PUT = 0
        loss_PUT = 0
        for j in stock_details:
            if j['percentage_id'] == OptionId_PUT and j['status'] == 'BUY' and j['call_put'] == "PUT" :
                setBuyCondition_PUT = False
                break
            else:
                setBuyCondition_PUT = True

            buy_time_PUT = j['buy_time']
            buyy_date_PUT = datetime.date(buy_time_PUT)

            today = date.today()
            if buyy_date_PUT == today and j['percentage_id'] == 3:
                if j['final_status'] == "PROFIT":
                    profit_PUT = profit_PUT + 1
                elif j['final_status'] == "LOSS":
                    loss_PUT = loss_PUT + 1
        if profit_PUT > loss_PUT:
            setOneStock_PUT = False
            print("YOU MAKE PROFIT TODAY IN BANKNIFTY PUT")
        else:
            setOneStock_PUT = True

        ## PCR CALL
        for i in stock_details:
            if i['percentage_id'] == OptionId_PCR_CALL and i['status'] == 'BUY' and i['call_put'] == "CALL" :
                setBuyCondition_PCR_CE = False
                break
            else:
                setBuyCondition_PCR_CE = True

        # PCR PUT
        for i in stock_details:
            if i['percentage_id'] == OptionId_PCR_PUT and i['status'] == 'BUY' and i['call_put'] == "PUT" :
                setBuyCondition_PCR_PUT = False
                break
            else:
                setBuyCondition_PCR_PUT = True

        for mx in PEMax:
            if PEMaxValue != CEMaxValue and cepeDiffrent >= 50000:
## CALL BUY
                if setOneStock_CALL == True:
                    if setBuyCondition_CALL == True:
                        if pcr >= set_CALL_pcr:
                            call_call = "CALL"
                            basePricePlus_CALL = mx['strikePrice'] + basePlus_CALL
                            basePricePlus_CALL_a = basePricePlus_CALL - 15
                            print('-------------------------------------------------------------------> BANKNIFTY CE:',basePricePlus_CALL_a,'<', livePrice,'<', basePricePlus_CALL)
                            if basePricePlus_CALL_a <= livePrice and livePrice <= basePricePlus_CALL:
                                BidPrice_CE = mx['CE']['bidprice']
                                squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                                stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                                sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                                stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                                strikePrice_CE = mx['strikePrice']
                                # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put':call_call}
                                if live_call == True:
                                    sellFun(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL)
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put =call_call, buy_pcr = '%.2f'% (pcr) )
                                print('SuccessFully Buy IN BANKNIFTY CALL: ',postData)

                        else:
                            print('YOU CAN BUY STOCK IN BANKNIFTY CALL: ')
                    else:
                        print("CAN'T BUY YOU HAVE STOCK OF BANKNIFTY CALL")

## PUT BUY
                if setOneStock_PUT == True:
                    if setBuyCondition_PUT == True:
                        if pcr <= set_PUT_pcr:
                            put_put = "PUT"
                            basePricePlus_PUT = mx['strikePrice'] + basePlus_PUT
                            basePricePlus_PUT_a = basePricePlus_PUT - 15
                            print('-------------------------------------------------------------------> BANKNIFTY PE:',basePricePlus_PUT_a, '<', livePrice, '<', basePricePlus_PUT )
                            if basePricePlus_PUT_a <= livePrice and livePrice <= basePricePlus_PUT:
                                BidPrice_PUT = mx['PE']['bidprice']
                                squareoff_PUT = '%.2f'% (( BidPrice_PUT * profitPercentage_PUT ) / 100)
                                stoploss_PUT = '%.2f'% ((BidPrice_PUT * lossPercentage_PUT ) / 100)
                                sellPrice_PUT = '%.2f'% ((BidPrice_PUT * profitPercentage_PUT) / 100 + BidPrice_PUT)
                                stop_loss_PUT = '%.2f'% (BidPrice_PUT - (BidPrice_PUT * lossPercentage_PUT ) / 100)
                                strikePrice_PUT = mx['strikePrice']
                                # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_PUT,live_brid_price=BidPrice_PUT , base_strike_price=strikePrice_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PUT ,stop_loseprice=stop_loss_PUT, percentage_id=OptionId_PUT , call_put =put_put, buy_pcr = '%.2f'% (pcr) )
                                postData = { "buy_price": BidPrice_PUT, "base_strike_price":strikePrice_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PUT, "stop_loseprice": stop_loss_PUT, 'percentage': OptionId_PUT, 'call_put':put_put}
                                if live_call == True:
                                    sellFun(strikePrice_PUT, BidPrice_PUT, squareoff_PUT, stoploss_PUT, OptionId_PUT, lot_size_PUT)

                                print('SuccessFully Buy IN BANKNIFTY PUT: ',postData)
                        else:
                            print('YOU CAN BUY STOCK IN BANKNIFTY PUT: ')
                    else:
                        print("CAN'T BUY YOU HAVE STOCK OF BANKNIFTY PUT")

## PCR CALL BUY
            if setBuyCondition_PCR_CE == True:
                pcr = '%.2f'% (pcr)
                pcr = float(pcr)
                print('YOU CAN BUY BANKNIFTY CALL IN PCR----->', set_call_pcr, '<', pcr)
                if set_call_pcr == pcr:
                    pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = True)
                else:
                    pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = False)

                if banknifty_at_set_pcr_CALL == True:
                    if set_call_pcr < pcr:
                        BidPrice_PCR_CALL = mx['CE']['bidprice']
                        sellPrice_PCR_CALL = '%.2f'% ((BidPrice_PCR_CALL * 10) / 100)
                        stop_loss_PCR_CALL = '%.2f'% ((BidPrice_PCR_CALL * 10 ) / 100)
                        pcr_StopLoss_CALL = pcr - 0.02
                        strikePrice_PCR_CALL = mx['strikePrice']
                        postData_PCR_CALL = { "buy_price": BidPrice_PCR_CALL,'PCR' : pcr, "base_strike_price":strikePrice_PCR_CALL, "live_Strike_price":livePrice, "sell_price": sellPrice_PCR_CALL, "stop_loseprice": stop_loss_PCR_CALL, 'percentage': OptionId_PCR_CALL, 'call_put' : 'CALL'}
                        # if live_call == True:
                        #     sellFun(strikePrice_PCR_CALL, BidPrice_PCR_CALL, sellPrice_PCR_CALL, stop_loss_PCR_CALL, OptionId_PCR_CALL, lot_size_pcr_call)
                        print('SuccessFully Buy in BANKNIFTY CALL at PCR =========> : ', postData_PCR_CALL)
                        pcr_option.objects.filter(id=PcrObj_Call_ID).update(LivePcr = '%.2f'% (pcr))
                        pcr_option.objects.filter(id=PcrObj_Call_ID).update(PcrStopLoss = '%.2f'% (pcr_StopLoss_CALL))
                        stock_detail.objects.create(status="BUY",buy_price = BidPrice_PCR_CALL,live_brid_price=BidPrice_PCR_CALL , base_strike_price=strikePrice_PCR_CALL, live_Strike_price=livePrice, sell_price= sellPrice_PCR_CALL ,stop_loseprice=stop_loss_PCR_CALL, percentage_id=OptionId_PCR_CALL , call_put = 'CALL', buy_pcr = '%.2f'% (pcr))
                        
# PCR PUT BUY
            if setBuyCondition_PCR_PUT == True:
                pcr = '%.2f'% (pcr)
                pcr = float(pcr)
                print('YOU CAN BUY BANKNIFTY PUT IN PCR----->', set_put_pcr, '>', pcr)
                if set_put_pcr == pcr:
                    pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = True)
                else:
                    pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)            
                
                if banknifty_at_set_pcr_PUT == True:
                    if set_put_pcr > pcr:
                        BidPrice_PCR_PUT = mx['PE']['bidprice']
                        sellPrice_PCR_PUT = '%.2f'% ((BidPrice_PCR_PUT * 10) / 100)
                        stop_loss_PCR_PUT = '%.2f'% ((BidPrice_PCR_PUT * 10 ) / 100)
                        pcr_StopLoss_PUT = pcr - 0.02
                        strikePrice_PCR_PUT = mx['strikePrice']
                        postData_PCR_PUT = { "buy_price": BidPrice_PCR_PUT, 'PCR' : pcr, "base_strike_price": strikePrice_PCR_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PCR_PUT, "stop_loseprice": stop_loss_PCR_PUT, 'percentage': OptionId_PCR_PUT, 'call_put' : 'PUT'}
                        # if live_call == True:
                        #     sellFun(strikePrice_PCR_PUT, BidPrice_PCR_PUT, sellPrice_PCR_PUT, stop_loss_PCR_PUT, OptionId_PCR_PUT, lot_size_pcr_put)
                        print('SuccessFully Buy in BANKNIFTY PUT at PCR =========> : ', postData_PCR_PUT)
                        pcr_option.objects.filter(id=PcrObj_Put_ID).update(LivePcr = '%.2f'% (pcr))
                        pcr_option.objects.filter(id=PcrObj_Put_ID).update(PcrStopLoss = '%.2f'% (pcr_StopLoss_PUT))
                        stock_detail.objects.create(status="BUY",buy_price = BidPrice_PCR_PUT, live_brid_price=BidPrice_PCR_PUT, base_strike_price=strikePrice_PCR_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PCR_PUT ,stop_loseprice=stop_loss_PCR_PUT, percentage_id=OptionId_PCR_PUT , call_put = 'PUT', buy_pcr = '%.2f'% (pcr))

        for sell in stock_details:
## CALL SELL
            if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_CALL and sell['call_put'] == 'CALL':
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
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status_admin_call, exit_pcr= '%.2f'% (pcr))
                            print("SuccessFully SELL STOCK OF CALL")
                
                        print('BANKNIFTY CALL-> ' ,'buy_pricee: ', buy_pricee, 'sell_Pricee: ', sell_Pricee, 'liveBidPrice: ', liveBidPrice, 'stop_Losss: ', stop_Losss)
                        if sell_Pricee <= liveBidPrice :
                            final_statuss = "PROFIT"
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True, exit_pcr= '%.2f'% (pcr))
                            print("SuccessFully SELL STOCK OF CALL")
                        if stop_Losss >= liveBidPrice:
                            final_statuss = "LOSS"
                            stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                            print("SuccessFully SELL STOCK OF CALL")
                        # pprint.pprint(stock_ID)
            
## PUT SELL
            if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_PUT and sell['call_put'] == 'PUT':
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
                            stock_detail.objects.filter(id=stock_ID_put).update(status = 'SELL', exit_price = liveBidPrice_put, sell_buy_time=sell_time_put, final_status = final_status_admin_PUT, exit_pcr= '%.2f'% (pcr))        
                            
                        print('BANKNIFTY PUT-> ' ,'buy_pricee: ', buy_pricee_put, 'sell_Pricee: ', sell_Pricee_put, 'liveBidPrice: ', liveBidPrice_put, 'stop_Losss: ', stop_Losss_put)
                        if sell_Pricee_put <= liveBidPrice_put :
                            final_statuss_put = "PROFIT"
                            stock_detail.objects.filter(id=stock_ID_put).update(status = 'SELL', exit_price = liveBidPrice_put, sell_buy_time=sell_time_put, final_status = final_statuss_put, admin_call = True, exit_pcr= '%.2f'% (pcr))        
                            print("SuccessFully SELL STOCK OF PUT")
                        if stop_Losss_put >= liveBidPrice_put:
                            final_statuss_put = "LOSS"
                            stock_detail.objects.filter(id=stock_ID_put).update(status = 'SELL', exit_price = liveBidPrice_put, sell_buy_time=sell_time_put, final_status = final_statuss_put, admin_call = True, exit_pcr= '%.2f'% (pcr))        
                            print("SuccessFully SELL STOCK OF PUT")
                            
## PCR CALL SELL
            if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_PCR_CALL and sell['call_put'] == 'CALL':
                strikePrice_SELL_BASE = sell['base_strike_price']
                for filters_BASE in filteredData:
                    if filters_BASE['strikePrice'] == strikePrice_SELL_BASE:
                        buy_pricee_BASE = sell['buy_price'] 
                        liveBidPrice_BASE = filters_BASE['CE']['bidprice']
                        stock_ID_BASE = sell['id']
                        sell_time_BASE = timezone.now()
                        pcr = '%.2f'% (pcr)
                        pcr = float(pcr)
                        if sell['admin_call'] == True and sell['status'] == 'BUY':
                            if buy_pricee_BASE < liveBidPrice_BASE:
                                final_status_admin_BASE = 'PROFIT'
                            else:
                                final_status_admin_BASE = 'LOSS'
                            print("SuccessFully SELL STOCK OF BANKNIFTY BASE")
                            pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = False)
                            stock_detail.objects.filter(id=stock_ID_BASE).update(status = 'SELL', exit_price = liveBidPrice_BASE, sell_buy_time=sell_time_BASE, final_status = final_status_admin_BASE, exit_pcr= '%.2f'% (pcr))
                        print("YOU HAVE A STOCK OF BANKNIFTY PCR CALL -->",'DB_pcr:', banknifty_pcr_stoploss_CALL, 'LivePCR:', pcr )
                        if banknifty_pcr_stoploss_CALL > pcr:
                            if buy_pricee_BASE < liveBidPrice_BASE:
                                final_status_admin_BASE = 'PROFIT'
                            else:
                                final_status_admin_BASE = 'LOSS'
                            print("SuccessFully SELL STOCK OF BANKNIFTY BASE")
                            pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = False)
                            stock_detail.objects.filter(id=stock_ID_BASE).update(status = 'SELL', exit_price = liveBidPrice_BASE, sell_buy_time=sell_time_BASE, final_status = final_status_admin_BASE, admin_call = True, exit_pcr= '%.2f'% (pcr))
                # pcr_option.objects.filter(id=1).update(banknifty_live_pcr = '%.2f'% (pcr))

## PCR PUT SELL
            if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_PCR_PUT and sell['call_put'] == 'PUT':
                strikePrice_SELL_PCR_PE = sell['base_strike_price']
                for filters_PCR_PE in filteredData:
                    if filters_PCR_PE['strikePrice'] == strikePrice_SELL_PCR_PE:
                        buy_pricee_PCR_PE = sell['buy_price'] 
                        liveBidPrice_PCR_PE = filters_PCR_PE['PE']['bidprice']
                        stock_ID_PCR_PE = sell['id']
                        sell_time_PCR_PE = timezone.now()
                        pcr = '%.2f'% (pcr)
                        pcr = float(pcr)
                        if sell['admin_call'] == True and sell['status'] == 'BUY':
                            if buy_pricee_PCR_PE < liveBidPrice_PCR_PE:
                                final_status_admin_PCR_PE = 'PROFIT'
                            else:
                                final_status_admin_PCR_PE = 'LOSS'
                            print("SuccessFully SELL STOCK OF BANKNIFTY PCR PUT")
                            pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)
                            stock_detail.objects.filter(id=stock_ID_PCR_PE).update(status = 'SELL', exit_price = liveBidPrice_PCR_PE, sell_buy_time=sell_time_PCR_PE, final_status = final_status_admin_PCR_PE, exit_pcr= '%.2f'% (pcr))
                        print("YOU HAVE A STOCK OF BANKNIFTY PCR PUT -->",'DB_pcr:', banknifty_pcr_stoploss_PUT, 'LivePCR:', pcr )
                        if banknifty_pcr_stoploss_PUT > pcr:
                            if buy_pricee_PCR_PE < liveBidPrice_PCR_PE:
                                final_status_admin_PCR_PE = 'PROFIT'
                            else:
                                final_status_admin_PCR_PE = 'LOSS'
                            print("SuccessFully SELL STOCK OF BANKNIFTY PCR PUT")
                            pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)
                            stock_detail.objects.filter(id=stock_ID_PCR_PE).update(status = 'SELL', exit_price = liveBidPrice_PCR_PE, sell_buy_time=sell_time_PCR_PE, final_status = final_status_admin_PCR_PE, admin_call = True, exit_pcr= '%.2f'% (pcr))
        pcr_option.objects.filter(id=PcrObj_Put_ID).update(LivePcr = '%.2f'% (pcr))

    except Exception as e:
        print('Error BankNifty -->', e)
        print("Connection refused by the server............................................. BANKNIFTY")