from nse_app.models import *
from django.utils import timezone
import datetime
import requests
import json
from datetime import date, datetime, timedelta
import pyotp
from smartapi import SmartConnect
import pandas as pd
from rich.console import Console
from .CoustomFun import Coustom
from .SellFunction import sellFunOption
consoleGreen = Console(style='green')
consoleBlue = Console(style='blue')
consoleRed = Console(style='red')


def NiftyApiFun():

    global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
    global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue, cepeDiffrent

    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                        'like Gecko) '
                        'Chrome/80.0.3987.149 Safari/537.36',
        'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    
    response = requests.get(url, headers=headers)
    data = response.text
    api_data = json.loads(data)

    filteredData = api_data['filtered']['data']
    timestamp = api_data['records']['timestamp']
    livePrice = api_data['records']['underlyingValue']


    down_price = Coustom.downPrice(filteredData, livePrice)

    up_price = Coustom.upPrice(filteredData, livePrice)
    
    downSliceList = Coustom.downMaxValue(down_price[:-6:-1])

    upSliceList = Coustom.upMaxValue(up_price[0:5])

    PEMax, PEMaxValue = Coustom.basePriceData(down_price, downSliceList)
    
    CEMax, CEMaxValue = Coustom.resistancePriceData(up_price, upSliceList)
            
    pcr = Coustom.pcrValue(api_data)
    
    for pe in PEMax:
        cepeDiffrent = pe['PE']['openInterest'] + pe['PE']['changeinOpenInterest'] - (pe['CE']['openInterest'] + pe['CE']['changeinOpenInterest'])
    cepeDiffrent = (cepeDiffrent)


    base_Price_down = []
    down_first_total_oi = ((down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']) - (down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest']))
    for downSlice3 in down_price[:-4:-1]:
        PE_oi_down = downSlice3['PE']['changeinOpenInterest'] + downSlice3['PE']['openInterest']
        CE_oi_down = downSlice3['CE']['changeinOpenInterest'] + downSlice3['CE']['openInterest']
        Total_oi_down = PE_oi_down - CE_oi_down
        if Total_oi_down > 50000:
            base_Price_down.append(downSlice3)
            break

    base_Price_up = []
    up_first_total_oi = ((up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']) - (up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest']))
    for upSlice3 in up_price[0:3]:
        PE_oi_up = upSlice3['PE']['changeinOpenInterest'] + upSlice3['PE']['openInterest']
        CE_oi_up = upSlice3['CE']['changeinOpenInterest'] + upSlice3['CE']['openInterest']
        Total_oi_up = PE_oi_up - CE_oi_up
        if abs(Total_oi_up) > 50000:
            base_Price_up.append(upSlice3)  
            break


def SettingFun():
    
    global stock_details, nseSetting, live_obj, pcr_options, live_call
    global PcrObj_Call_ID, nifty_pcr_stoploss, nifty_at_set_pcr_CALL, nifty_live_pcr, PcrObj_Put_ID, nifty_pcr_stoploss_PUT, nifty_at_set_pcr_PUT
    
    stock_details = stock_detail.objects.values_list().values()
    nseSetting = nse_setting.objects.values_list().values()
    live_obj = live.objects.values_list().values()
    live_call = live_obj[0]['live_nifty']
    pcr_options = pcr_option.objects.values_list().values()

    global set_CALL_pcr, basePlus_CALL, profitPercentage_CALL, lossPercentage_CALL, lot_size_CALL, lot_size_BASE, set_base_pcr
    global set_PUT_pcr, basePlus_PUT, profitPercentage_PUT, lossPercentage_PUT, lot_size_PUT, set_put_pcr, lot_size_pcr_put

    for pcrobj in pcr_options:
        if pcrobj['OptionName'] == 'NiftyPcrCALL':
            PcrObj_Call_ID = pcrobj['id']
            nifty_pcr_stoploss = pcrobj['PcrStopLoss']
            nifty_at_set_pcr_CALL = pcrobj['AtSetPcr']
            nifty_live_pcr = pcrobj['LivePcr']
        if pcrobj['OptionName'] == 'NiftyPcrPUT':
            PcrObj_Put_ID = pcrobj['id']
            nifty_pcr_stoploss_PUT = pcrobj['PcrStopLoss']
            nifty_at_set_pcr_PUT = pcrobj['AtSetPcr']
            nifty_live_pcr = pcrobj['LivePcr']        

    ## API SETTINGS
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
        if k['option'] == 'NIFTY_BASE_CE':
            set_base_pcr = k['set_pcr']
            lot_size_BASE = k['quantity_bn']
        if k['option'] == 'NIFTY_PCR_PE':
            set_put_pcr = k['set_pcr']
            lot_size_pcr_put = k['quantity_bn']

    global OptionId_CALL, OptionId_PUT, OptionId_PCR_CALL, OptionId_PCR_PUT


    for k in nseSetting:
        if k['option'] == "NIFTY CE":
            OptionId_CALL = k['id']
        if k['option'] == "NIFTY PE":
            OptionId_PUT = k['id']
        if k['option'] == "NIFTY_BASE_CE":
            OptionId_PCR_CALL = k['id']
        if k['option'] == "NIFTY_PCR_PE":
            OptionId_PCR_PUT = k['id']

    if stock_details.exists():
        pass
    else:
        now = datetime.now()
        yesterday = now - timedelta(days = 1)
        stock_details = [{'percentage_id':0, "status": '', "call_put":"",'buy_time':yesterday }]

    global setBuyCondition_CALL, setOneStock_CALL, setBuyCondition_PUT, setOneStock_PUT, setBuyCondition_PCR_CE, setBuyCondition_PCR_PUT

    ## CALL
    setBuyCondition_CALL, setOneStock_CALL = Coustom.buyCondition_withOneStock(stock_details, OptionId_CALL, "CALL", "NIFTY")
    ## PUT
    setBuyCondition_PUT, setOneStock_PUT = Coustom.buyCondition_withOneStock(stock_details, OptionId_PUT, "PUT", "NIFTY")
    ## PCR CALL
    setBuyCondition_PCR_CE = Coustom.buyCondition(stock_details, OptionId_PCR_CALL, "CALL")
    # PCR PUT
    setBuyCondition_PCR_PUT = Coustom.buyCondition(stock_details, OptionId_PCR_PUT, "PUT")


def NIFTY():
    global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
    global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue, cepeDiffrent
    # try:

    NiftyApiFun()
    SettingFun()

    ## CALL BUY
    if len(base_Price_down) != 0:
        for bpd in base_Price_down:
            if setOneStock_CALL == True:
                if setBuyCondition_CALL == True:
                    if pcr >= set_CALL_pcr:    
                        new_strike_price_CE = bpd['strikePrice']
                        new_strike_price_plus_CE = new_strike_price_CE + basePlus_CALL
                        new_strike_price_minus_CE = new_strike_price_plus_CE - 15
                        print('-------------------------------------------------------------------> NIFTY CE:', new_strike_price_minus_CE, '<', livePrice, '<', new_strike_price_plus_CE) 
                        if new_strike_price_minus_CE <= livePrice and livePrice <= new_strike_price_plus_CE:
                            # if abs(up_first_total_oi) <= 50000:
                                BidPrice_CE = bpd['CE']['bidprice']
                                squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                                stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                                sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                                stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                                strikePrice_CE = bpd['strikePrice']
                                # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put = "CALL", buy_pcr = '%.2f'% (pcr) )
                                postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put': "CALL"}
                                ## LIVE BUY
                                if live_call == True:
                                    sellFunOption(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL)
                                print('SuccessFully Buy IN NIFTY CALL: ',postData)    


    ## PUT BUY
    if len(base_Price_up) != 0:
        for bpu in base_Price_up:
            if setOneStock_PUT == True:
                if setBuyCondition_PUT == True:
                    if pcr <= set_PUT_pcr:
                        new_strike_price_PE = bpu['strikePrice']
                        new_strike_price_plus_PE = new_strike_price_PE + 10
                        new_strike_price_minus_PE = new_strike_price_PE - 10
                        print('-------------------------------------------------------------------> NIFTY PE:', new_strike_price_minus_PE, '<', livePrice, '<', new_strike_price_plus_PE)
                        if new_strike_price_minus_PE <= livePrice <= new_strike_price_plus_PE:
                            # if abs(down_first_total_oi) <= 50000:    
                                BidPrice_PUT = bpu['PE']['bidprice']
                                squareoff_PUT = '%.2f'% (( BidPrice_PUT * profitPercentage_PUT ) / 100)
                                stoploss_PUT = '%.2f'% ((BidPrice_PUT * lossPercentage_PUT ) / 100)
                                sellPrice_PUT = '%.2f'% ((BidPrice_PUT * profitPercentage_PUT) / 100 + BidPrice_PUT)
                                stop_loss_PUT = '%.2f'% (BidPrice_PUT - (BidPrice_PUT * lossPercentage_PUT ) / 100)
                                strikePrice_PUT = mx['strikePrice']
                                # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_PUT,live_brid_price=BidPrice_PUT , base_strike_price=strikePrice_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PUT ,stop_loseprice=stop_loss_PUT, percentage_id=OptionId_PUT , call_put = "PUT", buy_pcr = '%.2f'% (pcr) )
                                postData = { "buy_price": BidPrice_PUT, "base_strike_price":strikePrice_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PUT, "stop_loseprice": stop_loss_PUT, 'percentage': OptionId_PUT, 'call_put': "PUT"}
                                ## LIVE BUY
                                if live_call == True:
                                    sellFunOption(strikePrice_PUT, BidPrice_PUT, squareoff_PUT, stoploss_PUT, OptionId_PUT, lot_size_PUT)
                                print('SuccessFully Buy IN NIFTY PUT: ',postData)    

    for mx in PEMax:
        ## PCR CALL BUY
        if setBuyCondition_PCR_CE == True:
            if set_base_pcr != 0.0:
                pcr = '%.2f'% (pcr)
                pcr = float(pcr)
                print('YOU CAN BUY NIFTY CALL IN PCR----->', set_base_pcr, '<', pcr)
                if set_base_pcr == pcr:
                    pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = True)
                else:
                    pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = False)

                if nifty_at_set_pcr_CALL == True:
                    if set_base_pcr < pcr:
                        BidPrice_BASE = mx['CE']['bidprice']
                        sellPrice_BASE = '%.2f'% ((BidPrice_BASE * 10) / 100)
                        stop_loss_BASE = '%.2f'% ((BidPrice_BASE * 10 ) / 100)
                        pcr_StopLoss = pcr - 0.02
                        strikePrice_BASE = mx['strikePrice']
                        postData = { "buy_price": BidPrice_BASE,'PCR' : pcr, "base_strike_price":strikePrice_BASE, "live_Strike_price":livePrice, "sell_price": sellPrice_BASE, "stop_loseprice": stop_loss_BASE, 'percentage': OptionId_PCR_CALL, 'call_put' : 'CALL'}
                        ## LIVE BUY
                        if live_call == True:
                            sellFunOption(strikePrice_BASE, BidPrice_BASE, sellPrice_BASE, stop_loss_BASE, OptionId_PCR_CALL, lot_size_BASE)
                        print('SuccessFully Buy in NIFTY CALL at PCR : ', postData)
                        pcr_option.objects.filter(id=PcrObj_Call_ID).update(LivePcr = '%.2f'% (pcr))
                        pcr_option.objects.filter(id=PcrObj_Call_ID).update(PcrStopLoss = '%.2f'% (pcr_StopLoss))
                        stock_detail.objects.create(status="BUY",buy_price = BidPrice_BASE,live_brid_price=BidPrice_BASE , base_strike_price=strikePrice_BASE, live_Strike_price=livePrice, sell_price= sellPrice_BASE ,stop_loseprice=stop_loss_BASE, percentage_id=OptionId_PCR_CALL , call_put = 'CALL', buy_pcr = '%.2f'% (pcr) )

        # PCR PUT BUY
        if setBuyCondition_PCR_PUT == True:
            if set_put_pcr != 0.0:
                pcr = '%.2f'% (pcr)
                pcr = float(pcr)
                print('YOU CAN BUY NIFTY PUT IN PCR----->', set_put_pcr, '>', pcr)
                if set_put_pcr == pcr:
                    pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = True)
                else:
                    pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)            
                
                if nifty_at_set_pcr_PUT == True:
                    if set_put_pcr > pcr:
                        BidPrice_PCR_PUT = mx['PE']['bidprice']
                        sellPrice_PCR_PUT = '%.2f'% ((BidPrice_PCR_PUT * 10) / 100)
                        stop_loss_PCR_PUT = '%.2f'% ((BidPrice_PCR_PUT * 10 ) / 100)
                        pcr_StopLoss_PUT = pcr + 0.02
                        strikePrice_PCR_PUT = mx['strikePrice']
                        postData_PCR_PUT = { "buy_price": BidPrice_PCR_PUT, 'PCR' : pcr, "base_strike_price": strikePrice_PCR_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PCR_PUT, "stop_loseprice": stop_loss_PCR_PUT, 'percentage': OptionId_PCR_PUT, 'call_put' : 'PUT'}
                        if live_call == True:
                            sellFunOption(strikePrice_PCR_PUT, BidPrice_PCR_PUT, sellPrice_PCR_PUT, stop_loss_PCR_PUT, OptionId_PCR_PUT, lot_size_pcr_put)
                        print('SuccessFully Buy in NIFTY PUT at PCR =========> : ', postData_PCR_PUT)
                        pcr_option.objects.filter(id=PcrObj_Put_ID).update(LivePcr = '%.2f'% (pcr))
                        pcr_option.objects.filter(id=PcrObj_Put_ID).update(PcrStopLoss = '%.2f'% (pcr_StopLoss_PUT))
                        stock_detail.objects.create(status="BUY", percentage_id=OptionId_PCR_PUT, buy_price = BidPrice_PCR_PUT, live_brid_price=BidPrice_PCR_PUT, base_strike_price=strikePrice_PCR_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PCR_PUT ,stop_loseprice=stop_loss_PCR_PUT, call_put = 'PUT', buy_pcr = '%.2f'% (pcr))   


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
            
                    print('NIFTY CALL---> ' ,'buy_pricee: ', buy_pricee, 'sell_Pricee: ', sell_Pricee, 'liveBidPrice: ', liveBidPrice, 'stop_Losss: ', stop_Losss)
                    if sell_Pricee <= liveBidPrice :
                        final_statuss = "PROFIT"
                        stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_statuss, admin_call= True, exit_pcr= '%.2f'% (pcr))
                        print("SuccessFully SELL STOCK OF CALL")
                    if stop_Losss >= liveBidPrice:
                        final_statuss = "LOSS"
                        stock_detail.objects.filter(id=stock_ID).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_statuss,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                        print("SuccessFully SELL STOCK OF CALL")
        
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
                        
                    print('NIFTY PUT---> ' ,'buy_pricee: ', buy_pricee_put, 'sell_Pricee: ', sell_Pricee_put, 'liveBidPrice: ', liveBidPrice_put, 'stop_Losss: ', stop_Losss_put)
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
                        print("SuccessFully SELL STOCK OF NIFTY BASE")
                        pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = False)
                        stock_detail.objects.filter(id=stock_ID_BASE).update(status = 'SELL', exit_price = liveBidPrice_BASE, sell_buy_time=sell_time_BASE, final_status = final_status_admin_BASE, exit_pcr= '%.2f'% (pcr))
                    print("YOU HAVE A STOCK OF NIFTY PCR CALL ==============>",'StopLossPcr:', nifty_pcr_stoploss, '>=', 'LivePCR:', pcr )
                    if nifty_pcr_stoploss >= pcr:
                        if buy_pricee_BASE < liveBidPrice_BASE:
                            final_status_admin_BASE = 'PROFIT'
                        else:
                            final_status_admin_BASE = 'LOSS'
                        print("SuccessFully SELL STOCK OF NIFTY BASE")
                        pcr_option.objects.filter(id=PcrObj_Call_ID).update(AtSetPcr = False)
                        stock_detail.objects.filter(id=stock_ID_BASE).update(status = 'SELL', exit_price = liveBidPrice_BASE, sell_buy_time=sell_time_BASE, final_status = final_status_admin_BASE, admin_call = True, exit_pcr= '%.2f'% (pcr))            
    
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
                        print("SuccessFully SELL STOCK OF NIFTY PCR PUT")
                        pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)
                        stock_detail.objects.filter(id=stock_ID_PCR_PE).update(status = 'SELL', exit_price = liveBidPrice_PCR_PE, sell_buy_time=sell_time_PCR_PE, final_status = final_status_admin_PCR_PE, exit_pcr= '%.2f'% (pcr))
                    print("YOU HAVE A STOCK OF NIFTY PCR PUT ==============>",'StopLossPcr:', nifty_pcr_stoploss_PUT, '<=', 'LivePCR:', pcr )
                    if nifty_pcr_stoploss_PUT <= pcr:
                        if buy_pricee_PCR_PE < liveBidPrice_PCR_PE:
                            final_status_admin_PCR_PE = 'PROFIT'
                        else:
                            final_status_admin_PCR_PE = 'LOSS'
                        print("SuccessFully SELL STOCK OF NIFTY PCR PUT")
                        pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)
                        stock_detail.objects.filter(id=stock_ID_PCR_PE).update(status = 'SELL', exit_price = liveBidPrice_PCR_PE, sell_buy_time=sell_time_PCR_PE, final_status = final_status_admin_PCR_PE, admin_call = True, exit_pcr= '%.2f'% (pcr))
    pcr_option.objects.filter(id=PcrObj_Put_ID).update(LivePcr = '%.2f'% (pcr))        
        

    # except Exception as e:
        # consoleRed.print('Error-->', e)
        # consoleRed.print("Connection refused by the server...................................... NIFTY")



# def sellFun(strikePrice, BidPrice, squareoff, stoploss, OptionId, lots):
#     base_strike_price_sm = float(strikePrice)
#     buy_price_sm = str(BidPrice)
#     squareoff_sm = squareoff
#     stoploss_sm = stoploss
#     percentions_sm = OptionId
#     lot_size = lots

#     username = 'H117838'
#     apikey = 'SqtdCpAg'
#     pwd = '4689'
#     totp = pyotp.TOTP("K7QDKSEXWD7KRO7EVQCUHTFK2U").now()
#     obj = SmartConnect(api_key=apikey)
#     dataa = obj.generateSession(username, pwd, totp)

#     def place_order_pcr(token, symbol, qty,exch_seg ,buy_sell,ordertype ,price, variety='ROBO', triggerprice=5):
#         total_qty = float(qty) * lot_size
#         total_qty = int(total_qty)
#         total_qty = str(total_qty)
#         try:
#             orderparams = {
#                 "variety": 'NORMAL',
#                 "tradingsymbol": symbol,
#                 "symboltoken": token,
#                 "transactiontype": 'BUY',
#                 'exchange': 'NFO',
#                 "ordertype": 'LIMIT',
#                 "producttype": 'CARRYFORWARD',
#                 "duration": "DAY",
#                 "price": buy_price_sm,    
#                 "squareoff": '0',
#                 "stoploss": '0',
#                 "quantity":total_qty,
#             }
#             print(orderparams)
#             orderId = obj.placeOrder(orderparams)
#             print("The order id is: {}".format(orderId))
#             # stock_detail.objects.filter(id = get_id).update(orderid = orderId)
#         except Exception as e:
#             print(
#                 "Order placement failed: {}".format(e.message))    

#     def place_order(token, symbol, qty, buy_sell, ordertype, price, variety='ROBO', exch_seg='NFO', triggerprice=stoploss_sm):
#         total_qty = float(qty) * lot_size
#         total_qty = int(total_qty)
#         total_qty = str(total_qty)
#         try:
#             orderparams = {
#                 "variety": 'ROBO',
#                 "tradingsymbol": symbol,
#                 "symboltoken": token,
#                 "transactiontype": 'BUY',
#                 'exchange': 'NFO',
#                 "ordertype": 'LIMIT',
#                 "producttype": 'BO',
#                 "duration": "DAY",
#                 "price": buy_price_sm,
#                 "squareoff": squareoff_sm,
#                 "stoploss": stoploss_sm,
#                 "quantity": total_qty,
#                 "trailingStopLoss": "5",
#             }
#             print(orderparams)
#             orderId = obj.placeOrder(orderparams)
#             print("The order id is: {}".format(orderId))

#         except Exception as e:
#             print(
#                 "Order placement failed: {}".format(e.message))

#     url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
#     d = requests.get(url).json()
#     token_df = pd.DataFrame.from_dict(d)
#     token_df['expiry'] = pd.to_datetime(
#         token_df['expiry']).apply(lambda x: x.date())
#     token_df = token_df.astype({'strike': float})

#     def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):
#         df = token_df
#         strike_price = strike_price*100
#         if exch_seg == 'NSE':
#             eq_df = df[(df['exch_seg'] == 'NSE')]
#             return eq_df[eq_df['name'] == symbol]
#         elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
#             return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
#         elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
#             return df[(df['exch_seg'] == 'NFO') & (df['expiry'] == expiry_day) & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])

#     a = date(2023, 4, 6)

#     if percentions_sm == 3:
#         symbol = 'BANKNIFTY'
#         pe_strike_symbol = getTokenInfo(
#             symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', a).iloc[0]
#         place_order(pe_strike_symbol['token'], pe_strike_symbol['symbol'],
#                     pe_strike_symbol['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')

#     elif percentions_sm == 1:
#         symbol = 'BANKNIFTY'

#         ce_strike_symbol = getTokenInfo(
#             symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', a).iloc[0]
#         place_order(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
#                     ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

#     elif percentions_sm == 4:
#         symbol = 'NIFTY'
#         qty = 25
#         pe_strike_symbol = getTokenInfo(
#             symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', a).iloc[0]
#         place_order_pcr(pe_strike_symbol['token'], pe_strike_symbol['symbol'],
#                     pe_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO', qty)

#     elif percentions_sm == 2:
#         symbol = 'NIFTY'
#         ce_strike_symbol = getTokenInfo(
#             symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', a).iloc[0]
#         place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
#                     ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

#     elif percentions_sm == 8:
#         symbol = 'NIFTY'
#         ce_strike_symbol = getTokenInfo(
#             symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', a).iloc[0]
#         place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
#                     ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

#     elif percentions_sm == 10:
#         symbol = 'NIFTY'
#         ce_strike_symbol = getTokenInfo(
#             symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', a).iloc[0]
#         place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
#                     ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')


