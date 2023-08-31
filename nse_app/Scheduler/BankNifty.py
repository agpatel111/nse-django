from nse_app.models import *
from django.utils import timezone
import datetime
from datetime import datetime as dt
from datetime import date
import requests
import json
from datetime import timedelta
from rich.console import Console
from .CoustomFun import Coustom
from .SellFunction import sellFunOption, futureLivePrice

consoleGreen = Console(style='green')
consoleBlue = Console(style='blue')
consoleRed = Console(style='red')


# VARIABLES LOCAL AND SERVER BOTH ARE SAME
BANKNIFTY_CE = "BANKNIFTY CE"
BANKNIFTY_PE = "BANKNIFTY PE"
BANKNIFTY_PCR_CE = 'BANKNIFTY_BASE_CE'
BANKNIFTY_PCR_PE = 'BANKNIFTY_PCR_PE'
BANKNIFTY_FUTURE = 'BANKNIFTY FUTURE'

BANKNIFTY_URL = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

SETTINGS_URL = 'http://192.168.1.235:8000/settings'

def BankniftyApiFun():
    global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
    global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue, exprityDate
    

    # class InnerClass():
    #     def __init__(self, symbol = 'BANKNIFTY'):
    #         self.symbol = symbol
    #         self.headers = {
    #             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    #                         'Chrome/80.0.3987.149 Safari/537.36',
    #             'accept-language': 'en,gu;q=0.9,hi;q=0.8',
    #             'accept-encoding': 'gzip, deflate, br'
    #         }

    #     def fetch_data(self):
    #         url = f'https://www.nseindia.com/api/option-chain-indices?symbol={self.symbol}'
    #         response = requests.get(url, headers=self.headers)
    #         response.raise_for_status()
    #         data = response.json()
    #         return data
    # # InnerClass_ = InnerClass()
    # # print(InnerClass_.fetch_data())
    
    # def outer_function():
    #     class InnerClass:
    #         def __init__(self):
    #             self.value = 55
    #         def DEMO(self):
    #             print(self.value)
    #             self.value = self.value + 10
    #         def DEMO2(self):
    #             print(self.value)

    #     # inner_class = outer_function()
    #     instance = InnerClass()
    #     instance.DEMO()
    #     instance.DEMO2()
    # outer_function()
    # # print(instance.value)
            

    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

    url = BANKNIFTY_URL

    response = requests.get(url, headers=headers)
    data = response.text
    api_data = json.loads(data)
    
    
    timestamp = api_data['records']['timestamp']
    livePrice = api_data['records']['underlyingValue']
    filteredData = api_data['filtered']['data']

    date_string = api_data['records']['expiryDates'][0]
    date_format = "%d-%b-%Y"
    date_object = dt.strptime(date_string, date_format).date()
    exprityDate = date(date_object.year, date_object.month, date_object.day)


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
                else:
                    continue
            base_Price_down.append(downSlice3)
            break


    base_Price_up = []
    Total_oi_up_arr = []
    for upSlice3 in up_price[0:3]:
        PE_oi_up = upSlice3['PE']['changeinOpenInterest'] + upSlice3['PE']['openInterest']
        CE_oi_up = upSlice3['CE']['changeinOpenInterest'] + upSlice3['CE']['openInterest']
        Total_oi_up = PE_oi_up - CE_oi_up
        Total_oi_up_arr.append(Total_oi_up)
        if abs(Total_oi_up) > 50000:
            if abs(Total_oi_up_arr[0]) == abs(Total_oi_up):
                if down_first_total_oi < 50000:
                    base_Price_up.append(upSlice3)  
                    break 
                else:
                    continue
            base_Price_up.append(upSlice3)  
            break 

def SettingFun():
    
    global stock_details, nseSetting, live_obj, pcr_options, is_live_banknifty, is_op_fut_banknifty
    global PcrObj_Call_ID, banknifty_pcr_stoploss_CALL, banknifty_at_set_pcr_CALL, banknifty_live_pcr, PcrObj_Put_ID, banknifty_pcr_stoploss_PUT, banknifty_at_set_pcr_PUT

    ## SETTINGS 
    stock_details = stock_detail.objects.values().order_by("-buy_time")[:50]
    nseSetting = nse_setting.objects.values()
    live_obj = live.objects.values()
    # live_call = live_obj[0]['live_banknifty']
    pcr_options = pcr_option.objects.values()
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
    settings_url = SETTINGS_URL
    response = requests.get(settings_url)
    settings_data = response.text
    settings_data = json.loads(settings_data)
    settings_data_api = settings_data['data']
    is_live_banknifty = settings_data['liveSettings'][0]['live_banknifty']
    is_op_fut_banknifty = settings_data['liveSettings'][0]['op_fut_banknifty']
    
    global set_CALL_pcr, basePlus_CALL, profitPercentage_CALL, lossPercentage_CALL, lot_size_CALL, lot_size_pcr_call, set_call_pcr
    global set_PUT_pcr, basePlus_PUT, profitPercentage_PUT, lossPercentage_PUT, lot_size_PUT, set_put_pcr, lot_size_pcr_put
    global used_logic_put, used_logic_call

    for k in settings_data_api:
        if k['option'] == BANKNIFTY_CE:       ## Name as per server DB
            set_CALL_pcr = k['set_pcr']
            basePlus_CALL = k['baseprice_plus']
            profitPercentage_CALL = k['profit_percentage']
            lossPercentage_CALL = k['loss_percentage']
            lot_size_CALL = k['quantity_bn']
            used_logic_call = k['used_logic']
            oi_total_call = k['oi_total']
            
        if k['option'] == BANKNIFTY_PE:       ## Name as per server DB
            set_PUT_pcr = k['set_pcr']
            basePlus_PUT = k['baseprice_plus']
            profitPercentage_PUT = k['profit_percentage']
            lossPercentage_PUT = k['loss_percentage']
            lot_size_PUT = k['quantity_bn'] 
            used_logic_put = k['used_logic']
            oi_total_put = k['oi_total']
            
        if k['option'] == BANKNIFTY_PCR_CE:       ## Name as per server DB
            set_call_pcr = k['set_pcr']
            lot_size_pcr_call = k['quantity_bn']
            
        if k['option'] == BANKNIFTY_PCR_PE:       ## Name as per server DB
            set_put_pcr = k['set_pcr']
            lot_size_pcr_put = k['quantity_bn']
            
            
    global OptionId_CALL, OptionId_PUT, OptionId_PCR_CALL, OptionId_PCR_PUT, OptionId_Future

    for k in nseSetting:
        if k['option'] == BANKNIFTY_CE:       ## Name as per Local DB
            OptionId_CALL = k['id']
        if k['option'] == BANKNIFTY_PE:       ## Name as per Local DB
            OptionId_PUT = k['id']
        if k['option'] == BANKNIFTY_PCR_CE:       ## Name as per Local DB
            OptionId_PCR_CALL = k['id']
        if k['option'] == BANKNIFTY_PCR_PE:       ## Name as per Local DB
            OptionId_PCR_PUT = k['id']        
        if k['option'] == BANKNIFTY_FUTURE:       ## Name as per Local DB
            OptionId_Future = k['id']        
        
    if stock_details.exists():
        pass
    else:
        now = datetime.now()
        yesterday = now - timedelta(days = 1)
        stock_details = [{'percentage_id':0, "status": '', "call_put":"", 'buy_time':yesterday }]


    global setBuyCondition_CALL, setOneStock_CALL, setBuyCondition_PUT, setOneStock_PUT, setBuyCondition_PCR_CE, setBuyCondition_PCR_PUT
    
    ## CALL Buy Condition
    setBuyCondition_CALL, setOneStock_CALL = Coustom.buyCondition_withOneStock(stock_details, OptionId_CALL, "CALL", "BANKNIFTY")
    ## PUT Buy Condition
    setBuyCondition_PUT, setOneStock_PUT = Coustom.buyCondition_withOneStock(stock_details, OptionId_PUT, "PUT", "BANKNIFTY")
    ## PCR CALL Buy Condition
    setBuyCondition_PCR_CE = Coustom.buyCondition(stock_details, OptionId_PCR_CALL, "CALL")
    # PCR PUT Buy Condition
    setBuyCondition_PCR_PUT = Coustom.buyCondition(stock_details, OptionId_PCR_PUT, "PUT")


def BANKNIFTY():
    current_time = datetime.datetime.now().time()
    start_time = datetime.time(hour=9, minute=40)
    end_time = datetime.time(hour=22, minute=20)
    
    if start_time <= current_time <= end_time:
        global api_data, livePrice, timestamp, filteredData, PEMax, CEMax, down_price, up_price, downSliceList, upSliceList, pcr, base_Price_down, base_Price_up
        global up_first_total_oi, down_first_total_oi, CEMaxValue, PEMaxValue, exprityDate, OptionId_Future, is_op_fut_banknifty
        
        file = open("bank_nifty.txt", "a")
        try:
            BankniftyApiFun()

            SettingFun()
            
            def process_logic_call(used_logic_call, base_Price_down, setOneStock_CALL, setBuyCondition_CALL, set_CALL_pcr, livePrice,
                                basePlus_CALL, profitPercentage_CALL, lossPercentage_CALL, OptionId_CALL, pcr):
                pass

            if used_logic_call == 'old':
                for nbpd in base_Price_down:
                    if setOneStock_CALL == True:
                        if setBuyCondition_CALL == True:
                            if pcr >= set_CALL_pcr:
                                call_call = "CALL"
                                basePricePlus_CALL = nbpd['strikePrice'] + basePlus_CALL
                                basePricePlus_CALL_a = basePricePlus_CALL - 15
                                print('-------------------------------------------------------------------> BANKNIFTY CE:',basePricePlus_CALL_a,'<', livePrice,'<', basePricePlus_CALL)
                                if basePricePlus_CALL_a <= livePrice and livePrice <= basePricePlus_CALL:
                                    BidPrice_CE = nbpd['CE']['bidprice']
                                    squareoff_CE = '%.2f'% (( BidPrice_CE * profitPercentage_CALL ) / 100)
                                    stoploss_CE = '%.2f'% ((BidPrice_CE * lossPercentage_CALL ) / 100)
                                    sellPrice_CE = '%.2f'% ((BidPrice_CE * profitPercentage_CALL) / 100 + BidPrice_CE)
                                    stop_loss_CE = '%.2f'% (BidPrice_CE - (BidPrice_CE * lossPercentage_CALL ) / 100)
                                    strikePrice_CE = nbpd['strikePrice']
                                    # <------------------------------  ADD DATA TO DATABASE  ---------------------------------->
                                    obj_banknifty_old = stock_detail.objects.create(status="BUY",buy_price = BidPrice_CE, base_strike_price=strikePrice_CE, live_Strike_price=livePrice, live_brid_price=BidPrice_CE, sell_price= sellPrice_CE ,stop_loseprice=stop_loss_CE, percentage_id=OptionId_CALL , call_put =call_call, buy_pcr = '%.2f'% (pcr) )
                                    postData = { "buy_price": BidPrice_CE, "base_strike_price":strikePrice_CE, "live_Strike_price":livePrice, "sell_price": sellPrice_CE, "stop_loseprice": stop_loss_CE, 'percentage': OptionId_CALL, 'call_put':call_call}
                                    # if is_live_banknifty == True:
                                    #     if is_op_fut_banknifty == 'OPTION':
                                    #         sellFunOption(strikePrice_CE, BidPrice_CE, squareoff_CE, stoploss_CE, OptionId_CALL, lot_size_CALL, obj_banknifty_old.id, exprityDate)
                                    #     elif is_op_fut_banknifty == 'FUTURE':
                                    #         pass
                                    print('SuccessFully Buy IN BANKNIFTY CALL: ', postData)                     
                 
                        
            if used_logic_put == 'old':
                pass           
           
                                   

            def bidPrice(filteredData, strikePrice, ce_pe):
                for i in filteredData:
                    if strikePrice == i['strikePrice']:
                        return i[ce_pe]['bidprice']

            
            def sell_stock_logic(stock_data, optionId, filteredData,  pcr):
                sell_time = timezone.now()
                for i in stock_data:
                    if i['status'] == 'BUY' and i['percentage_id'] == optionId:
                        id = i['id'] 
                        buy_price = i['buy_price'] 
                        sell_price = i['sell_price']
                        stop_loseprice = i['stop_loseprice']
                        strikePrice = i['base_strike_price']
                        if i['call_put'] == 'CALL': ce_pe = 'CE'
                        elif i['call_put'] == 'PUT': ce_pe = 'PE'
                        liveBidPrice = (bidPrice(filteredData, strikePrice, ce_pe))
                        
                        print('BANKNIFTY', ce_pe, '--->', 'buy_price: ', buy_price, 'sell_Pricee: ', sell_price, 'liveBidPrice: ', liveBidPrice, 'stop_Losss: ', stop_loseprice)
                        if i['admin_call'] == True:
                            if buy_price < liveBidPrice:
                                final_status = 'PROFIT'
                            else:
                                final_status = 'LOSS'
                            stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                            print("SuccessFully SELL STOCK OF", ce_pe)

                        if sell_price <= liveBidPrice :
                            final_status = "PROFIT"
                            stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                            print("SuccessFully SELL STOCK OF",ce_pe)
                        if stop_loseprice >= liveBidPrice:
                            final_status = "LOSS"
                            stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = liveBidPrice, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                            print("SuccessFully SELL STOCK OF", ce_pe)
                                
            ## CALL SELL                    
            sell_stock_logic(stock_details, OptionId_CALL, filteredData, pcr)
            ## PUT SELL
            sell_stock_logic(stock_details, OptionId_PUT, filteredData, pcr)

            # #SELL STOCKS
            for sell in stock_details:
                                     
                ## FUTURE SELL
                if sell['status'] == 'BUY' and sell['percentage_id'] == OptionId_Future:
                    sell_time = timezone.now()
                    buy_price = sell['buy_price']
                    sell_price = sell['sell_price']
                    stop_loseprice = sell['stop_loseprice']
                    futureLive = futureLivePrice('BANKNIFTY')
                    id = sell['id']
                    
                    print('BANKNIFTY FUTURE--->', 'buy_price: ', buy_price, 'sell_Pricee: ', sell_price, 'liveBidPrice: ', futureLive, 'stop_Losss: ', stop_loseprice)
                    if sell_price <= futureLive :
                        final_status = "PROFIT"
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, admin_call= True, exit_pcr= '%.2f'% (pcr))
                        print("SuccessFully SELL STOCK OF FUTURE")
                    if stop_loseprice >= futureLive:
                        final_status = "LOSS"
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status,admin_call = True, exit_pcr= '%.2f'% (pcr) )
                        print("SuccessFully SELL STOCK OF FUTURE")
                    if sell['admin_call'] == True:
                        if buy_price < futureLive:
                            final_status = 'PROFIT'
                        else:
                            final_status = 'LOSS'
                        stock_detail.objects.filter(id=id).update(status = 'SELL', exit_price = futureLive, sell_buy_time=sell_time, final_status = final_status, exit_pcr= '%.2f'% (pcr))
                        print("SuccessFully SELL STOCK OF")


        except Exception as e:
            file.write(str(e) + "\n")
            consoleRed.print('Error BankNifty -->', e)
            consoleRed.print("Connection refused by the server............................................. BANKNIFTY")

        file.close()
