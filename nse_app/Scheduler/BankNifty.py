from nse_app.models import *
from django.utils import timezone
import datetime
import requests
import json
from datetime import timedelta
from rich.console import Console
from .CoustomFun import Coustom
from .SellFunction import sellFunOption
consoleGreen = Console(style='green')
consoleBlue = Console(style='blue')
consoleRed = Console(style='red')



def BankniftyApiFun():
    global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
    global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue
    
    
    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

    response = requests.get(url, headers=headers)
    data = response.text
    api_data = json.loads(data)
    
    
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
            
    down_first_total_oi = ((down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']) - (down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest']))
    up_first_total_oi = ((up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']) - (up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest']))

    base_Price_down = []
    Total_oi_down_arr = []
    for downSlice3 in down_price[:-4:-1]:
        PE_oi_down = downSlice3['PE']['changeinOpenInterest'] + downSlice3['PE']['openInterest']
        CE_oi_down = downSlice3['CE']['changeinOpenInterest'] + downSlice3['CE']['openInterest']
        Total_oi_down = PE_oi_down - CE_oi_down
        Total_oi_down_arr.append(Total_oi_down)
        if Total_oi_down > 50000:
            if abs(Total_oi_down_arr[0]) == abs(Total_oi_down):
                if up_first_total_oi < 50000:
                    base_Price_down.append(downSlice3)
                    break
            base_Price_down.append(downSlice3)
            break


    base_Price_up = []
    for upSlice3 in up_price[0:3]:
        PE_oi_up = upSlice3['PE']['changeinOpenInterest'] + upSlice3['PE']['openInterest']
        CE_oi_up = upSlice3['CE']['changeinOpenInterest'] + upSlice3['CE']['openInterest']
        Total_oi_up = PE_oi_up - CE_oi_up
        if abs(Total_oi_up) > 50000:
            base_Price_up.append(upSlice3)  
            break 


def SettingFun():
    
    global stock_details, nseSetting, live_obj, pcr_options, live_call
    global PcrObj_Call_ID, banknifty_pcr_stoploss_CALL, banknifty_at_set_pcr_CALL, banknifty_live_pcr, PcrObj_Put_ID, banknifty_pcr_stoploss_PUT, banknifty_at_set_pcr_PUT

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
    
    global set_CALL_pcr, basePlus_CALL, profitPercentage_CALL, lossPercentage_CALL, lot_size_CALL, lot_size_pcr_call, set_call_pcr
    global set_PUT_pcr, basePlus_PUT, profitPercentage_PUT, lossPercentage_PUT, lot_size_PUT, set_put_pcr, lot_size_pcr_put

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
            
            
    global OptionId_CALL, OptionId_PUT, OptionId_PCR_CALL, OptionId_PCR_PUT

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
        stock_details = [{'percentage_id':0, "status": '', "call_put":"", 'buy_time':yesterday }]


    global setBuyCondition_CALL, setOneStock_CALL, setBuyCondition_PUT, setOneStock_PUT, setBuyCondition_PCR_CE, setBuyCondition_PCR_PUT
    
    ## CALL
    setBuyCondition_CALL, setOneStock_CALL = Coustom.buyCondition_withOneStock(stock_details, OptionId_CALL, "CALL", "BANKNIFTY")
    ## PUT
    setBuyCondition_PUT, setOneStock_PUT = Coustom.buyCondition_withOneStock(stock_details, OptionId_PUT, "PUT", "BANKNIFTY")
    ## PCR CALL
    setBuyCondition_PCR_CE = Coustom.buyCondition(stock_details, OptionId_PCR_CALL, "CALL")
    # PCR PUT
    setBuyCondition_PCR_PUT = Coustom.buyCondition(stock_details, OptionId_PCR_PUT, "PUT")


def BANKNIFTY():
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(hour=9, minute=15)
    end_time = datetime.time(hour=15, minute=30)
    if start_time <= current_time <= end_time:
        global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
        global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue
        
        try:
            BankniftyApiFun()

            SettingFun()
            
            if len(base_Price_down) != 0:
                for nbpd in base_Price_down:
                    if setBuyCondition_CALL == True:
                        base_zone_obj = BaseZoneBanknifty.objects.all().values() 
                        
                        liveDbPrice = LiveDataBankNifty.objects.all().order_by('-id').values()
                        liveDbPrice = liveDbPrice[0]
                        new_strike_price_CE_ = nbpd['strikePrice']
                        new_strike_price_plus_CE_ = new_strike_price_CE_ + basePlus_CALL
                        new_strike_price_minus_CE_ = new_strike_price_CE_ - 15
                        
                        if len(base_zone_obj) == 0:
                            if liveDbPrice['in_basezone'] == False:
                                print('-------------------------------------------------------------------> BANKNIFTY CE:', new_strike_price_minus_CE_, '<', livePrice, '<', new_strike_price_plus_CE_)
                                if new_strike_price_minus_CE_ < livePrice < new_strike_price_plus_CE_:
                                    BaseZoneBanknifty.objects.create(in_basezone = True, base_price = new_strike_price_plus_CE_ , stop_loss_price=new_strike_price_minus_CE_)
                        else:
                            consoleBlue.print('--------------------------- BANKNIFTY IN  BUYZONE ---->')
                            base_zone_obj = base_zone_obj[0]
                            base_price = base_zone_obj['base_price']
                            if liveDbPrice['in_basezone'] == True:
                                last_live_price = liveDbPrice['live_price']
                                
                                if base_price < last_live_price:
                                    BidPrice_CE = nbpd['CE']['bidprice']
                                    squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                                    stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                                    sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                                    stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                                    strikePrice_CE = nbpd['strikePrice']
                                    ## ADD DATA TO DATABASE 
                                    postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put': "CALL"}
                                    stock_detail.objects.create(status="BUY",buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put = "CALL", buy_pcr = '%.2f'% (pcr) )
                                    print('SuccessFully Buy IN BANKNIFTY CALL: ',postData)                
                                    ## SMART API BUY FUNCTION
                                    if live_call == True:
                                        sellFunOption(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL)
                                    
                                    LiveDataBankNifty.objects.filter(id = liveDbPrice['id']).update(in_basezone = False)
                                    BaseZoneBanknifty.objects.all().delete()
                                    consoleGreen.print('SuccessFully BUY---------------------------------->', livePrice)
                                else:
                                    BaseZoneBanknifty.objects.all().delete()
                                    LiveDataBankNifty.objects.filter(id = liveDbPrice['id']).update(in_basezone = False)
                            
                            
                            
                            

            # ## CALL BUY
            # if len(base_Price_down) != 0:
            #     for bpd in base_Price_down:
            #         if setOneStock_CALL == True:
            #             if setBuyCondition_CALL == True:
            #                 if pcr >= set_CALL_pcr:
            #                     new_strike_price_CE = bpd['strikePrice']
            #                     new_strike_price_plus_CE = new_strike_price_CE + basePlus_CALL
            #                     new_strike_price_minus_CE = new_strike_price_plus_CE - 15
            #                     print('-------------------------------------------------------------------> BANKNIFTY CE:', new_strike_price_minus_CE, '<', livePrice, '<', new_strike_price_plus_CE)
            #                     if new_strike_price_minus_CE <= livePrice <= new_strike_price_plus_CE:
            #                         # if abs(up_first_total_oi) <= 50000:
            #                             BidPrice_CE = bpd['CE']['bidprice']
            #                             squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
            #                             stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
            #                             sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
            #                             stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
            #                             strikePrice_CE = bpd['strikePrice']
            #                             # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
            #                             postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put': "CALL"}
            #                             ## LIVE BUY
            #                             if live_call == True:
            #                                 sellFunOption(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL)
            #                             stock_detail.objects.create(status="BUY",buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put = "CALL", buy_pcr = '%.2f'% (pcr) )
            #                             print('SuccessFully Buy IN BANKNIFTY CALL: ',postData)                
            
            ## PUT BUY
            if len(base_Price_up) != 0:
                for bpu in base_Price_up:
                    if setOneStock_PUT == True:
                        if setBuyCondition_PUT == True:
                            if pcr <= set_PUT_pcr:
                                new_strike_price_PE = bpu['strikePrice']
                                new_strike_price_plus_PE = new_strike_price_PE + 10
                                new_strike_price_minus_PE = new_strike_price_PE - 10
                                print('-------------------------------------------------------------------> BANKNIFTY PE:', new_strike_price_minus_PE, '<', livePrice, '<', new_strike_price_plus_PE)
                                if new_strike_price_minus_PE <= livePrice <= new_strike_price_plus_PE:
                                    # if abs(down_first_total_oi) <= 50000:
                                        BidPrice_PUT = bpu['PE']['bidprice']
                                        strikePrice_PUT = bpu['strikePrice']
                                        squareoff_PUT = '%.2f'% (( BidPrice_PUT * profitPercentage_PUT ) / 100)
                                        stoploss_PUT = '%.2f'% ((BidPrice_PUT * lossPercentage_PUT ) / 100)
                                        sellPrice_PUT = '%.2f'% ((BidPrice_PUT * profitPercentage_PUT) / 100 + BidPrice_PUT)
                                        stop_loss_PUT = '%.2f'% (BidPrice_PUT - (BidPrice_PUT * lossPercentage_PUT ) / 100)
                                        ## ADD DATA TO DATABASE 
                                        stock_detail.objects.create(status="BUY",buy_price = BidPrice_PUT,live_brid_price=BidPrice_PUT , base_strike_price=strikePrice_PUT, live_Strike_price=livePrice, sell_price= sellPrice_PUT ,stop_loseprice=stop_loss_PUT, percentage_id=OptionId_PUT , call_put = "PUT", buy_pcr = '%.2f'% (pcr) )
                                        postData = { "buy_price": BidPrice_PUT, "base_strike_price":strikePrice_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PUT, "stop_loseprice": stop_loss_PUT, 'percentage': OptionId_PUT, 'call_put': "PUT"}
                                        ## LIVE BUY
                                        if live_call == True:
                                            sellFunOption(strikePrice_PUT, BidPrice_PUT, squareoff_PUT, stoploss_PUT, OptionId_PUT, lot_size_PUT)
                                        print('SuccessFully Buy IN BANKNIFTY PUT: ',postData)


            
            for mx in PEMax:
                ## PCR CALL BUY
                if setBuyCondition_PCR_CE == True:
                    if set_call_pcr != 0.0:
                        pcr = '%.2f'% (pcr)
                        pcr = float(pcr)
                        print('----------------------------------->BANKNIFTY CALL PCR: ', set_call_pcr, '<', pcr)
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
                                if live_call == True:
                                    sellFunOption(strikePrice_PCR_CALL, BidPrice_PCR_CALL, sellPrice_PCR_CALL, stop_loss_PCR_CALL, OptionId_PCR_CALL, lot_size_pcr_call)
                                print('SuccessFully Buy in BANKNIFTY CALL at PCR =========> : ', postData_PCR_CALL)
                                pcr_option.objects.filter(id=PcrObj_Call_ID).update(LivePcr = '%.2f'% (pcr))
                                pcr_option.objects.filter(id=PcrObj_Call_ID).update(PcrStopLoss = '%.2f'% (pcr_StopLoss_CALL))
                                stock_detail.objects.create(status="BUY",buy_price = BidPrice_PCR_CALL,live_brid_price=BidPrice_PCR_CALL , base_strike_price=strikePrice_PCR_CALL, live_Strike_price=livePrice, sell_price= sellPrice_PCR_CALL ,stop_loseprice=stop_loss_PCR_CALL, percentage_id=OptionId_PCR_CALL , call_put = 'CALL', buy_pcr = '%.2f'% (pcr))

                ## PUT PCR BUY
                if setBuyCondition_PCR_PUT == True:
                    if set_put_pcr != 0.0:
                        pcr = '%.2f'% (pcr)
                        pcr = float(pcr)
                        print('----------------------------------->BANKNIFTY PUT PCR: ', set_put_pcr, '>', pcr)
                        if set_put_pcr == pcr:
                            pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = True)
                        else:
                            pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)            
                        
                        if banknifty_at_set_pcr_PUT == True:
                            if set_put_pcr > pcr:
                                BidPrice_PCR_PUT = mx['PE']['bidprice']
                                sellPrice_PCR_PUT = '%.2f'% ((BidPrice_PCR_PUT * 10) / 100)
                                stop_loss_PCR_PUT = '%.2f'% ((BidPrice_PCR_PUT * 10 ) / 100)
                                pcr_StopLoss_PUT = pcr + 0.02
                                strikePrice_PCR_PUT = mx['strikePrice']
                                postData_PCR_PUT = { "buy_price": BidPrice_PCR_PUT, 'PCR' : pcr, "base_strike_price": strikePrice_PCR_PUT, "live_Strike_price":livePrice, "sell_price": sellPrice_PCR_PUT, "stop_loseprice": stop_loss_PCR_PUT, 'percentage': OptionId_PCR_PUT, 'call_put' : 'PUT'}
                                if live_call == True:
                                    sellFunOption(strikePrice_PCR_PUT, BidPrice_PCR_PUT, sellPrice_PCR_PUT, stop_loss_PCR_PUT, OptionId_PCR_PUT, lot_size_pcr_put)
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
                    
                            print('BANKNIFTY CALL---> ' ,'buy_pricee: ', buy_pricee, 'sell_Pricee: ', sell_Pricee, 'liveBidPrice: ', liveBidPrice, 'stop_Losss: ', stop_Losss)
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
                                
                            print('BANKNIFTY PUT---> ' ,'buy_pricee: ', buy_pricee_put, 'sell_Pricee: ', sell_Pricee_put, 'liveBidPrice: ', liveBidPrice_put, 'stop_Losss: ', stop_Losss_put)
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
                            print("YOU HAVE A STOCK OF BANKNIFTY PCR CALL ==============>",'StopLossPcr:', banknifty_pcr_stoploss_CALL, '>=', 'LivePCR:', pcr )
                            if banknifty_pcr_stoploss_CALL >= pcr:
                                if buy_pricee_BASE < liveBidPrice_BASE:
                                    final_status_admin_BASE = 'PROFIT'
                                else:
                                    final_status_admin_BASE = 'LOSS'
                                print("SuccessFully SELL STOCK OF BANKNIFTY BASE")
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
                                print("SuccessFully SELL STOCK OF BANKNIFTY PCR PUT")
                                pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)
                                stock_detail.objects.filter(id=stock_ID_PCR_PE).update(status = 'SELL', exit_price = liveBidPrice_PCR_PE, sell_buy_time=sell_time_PCR_PE, final_status = final_status_admin_PCR_PE, exit_pcr= '%.2f'% (pcr))
                            print("YOU HAVE A STOCK OF BANKNIFTY PCR PUT ==============>",'StopLossPcr:', banknifty_pcr_stoploss_PUT, '<=', 'LivePCR:', pcr )
                            if banknifty_pcr_stoploss_PUT <= pcr:
                                if buy_pricee_PCR_PE < liveBidPrice_PCR_PE:
                                    final_status_admin_PCR_PE = 'PROFIT'
                                else:
                                    final_status_admin_PCR_PE = 'LOSS'
                                print("SuccessFully SELL STOCK OF BANKNIFTY PCR PUT")
                                pcr_option.objects.filter(id=PcrObj_Put_ID).update(AtSetPcr = False)
                                stock_detail.objects.filter(id=stock_ID_PCR_PE).update(status = 'SELL', exit_price = liveBidPrice_PCR_PE, sell_buy_time=sell_time_PCR_PE, final_status = final_status_admin_PCR_PE, admin_call = True, exit_pcr= '%.2f'% (pcr))
            pcr_option.objects.filter(id=PcrObj_Put_ID).update(LivePcr = '%.2f'% (pcr))

        except Exception as e:
            consoleRed.print('Error BankNifty -->', e)
            consoleRed.print("Connection refused by the server............................................. BANKNIFTY")

