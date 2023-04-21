import requests
import json
from datetime import datetime
from nse_app.models import *
from .CoustomFun import Coustom

def PcrValues():
    current_time = datetime.now()
    current_time = current_time.strftime("%H:%M")
    times =  [
        '9:15',
        '9:30',
        '9:45',
        '10:00',
        '10:15',
        '10:30',
        '10:45',
        '11:00',
        '11:15',
        '11:30',
        '11:45',
        '12:00',
        '12:15',
        '12:30',
        '12:45',
        '13:00',
        '13:15',
        '13:30',
        '13:45',
        '14:00',
        '14:15',
        '14:30',
        '14:45',
        '15:00',
        '15:15',
        '15:30',
     ] 


    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                    'like Gecko) '
                    'Chrome/80.0.3987.149 Safari/537.36',
    'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    
    
    ### ------------------------ BANK NIFTY ------------------------------------
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
    response = requests.get(url, headers=headers)
    data = response.text
    api_data = json.loads(data)
    
    ## PCR
    pcr = Coustom.pcrValue(api_data)
    if current_time in times:
        pcr_values.objects.create(option_name='BANKNIFTY', pcr_value=pcr)
        print('Pcr BankNifty->', pcr)

    ## LIVE PRICE
    livePrice_banknifty = api_data['records']['underlyingValue']
    base_zone_obj = BaseZoneBanknifty.objects.all().values() 
    if len(base_zone_obj) != 0:
        if base_zone_obj[0]['in_basezone'] == True:
            if current_time in times:
                LiveDataBankNifty.objects.create(live_price = livePrice_banknifty, in_basezone=True)
                print("LiveData Added successfully BankNifty", livePrice_banknifty)
    else:
        if current_time in times:
            LiveDataBankNifty.objects.create(live_price = livePrice_banknifty)
            print(current_time in times)
            print("LiveData Added successfully BankNifty", livePrice_banknifty)
     

    ### ------------------------ NIFTY ------------------------------------
    url_nifty = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    response_nifty = requests.get(url_nifty, headers=headers)
    data_nifty = response_nifty.text
    api_data_nifty = json.loads(data_nifty)
    
    ## PCR
    pcr_nifty = Coustom.pcrValue(api_data_nifty)
    if current_time in times:
        pcr_values.objects.create(option_name='NIFTY', pcr_value=pcr_nifty)
        print('Pcr Nifty->', pcr_nifty)
        
    ## LIVE PRICE
    livePrice_nifty = api_data_nifty['records']['underlyingValue']
    base_zone_obj_nifty = BaseZoneNifty.objects.all().values() 
    if len(base_zone_obj_nifty) != 0:
        if base_zone_obj_nifty[0]['in_basezone'] == True:
            if current_time in times:
                LiveDataNifty.objects.create(live_price = livePrice_nifty, in_basezone=True)
                print("LiveData Added successfully Nifty", livePrice_nifty)
        
    else:
        if current_time in times:
            LiveDataNifty.objects.create(live_price = livePrice_nifty)
            print(current_time in times)
            print("LiveData Added successfully Nifty", livePrice_nifty)
    

# def LivePriceFun():
#     headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
#                             'like Gecko) '
#                             'Chrome/80.0.3987.149 Safari/537.36',
#             'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}

#     url = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'

#     response = requests.get(url, headers=headers)
#     data = response.text
#     api_data = json.loads(data)
    
#     timestamp = api_data['records']['timestamp']
#     current_time = datetime.now()
#     current_time = current_time.strftime("%H:%M")
#     times =  [
#         '9:15',
#         '9:30',
#         '9:45',
#         '10:00',
#         '10:15',
#         '10:21',
#         '10:30',
#         '11:00',
#         '11:15',
#         '11:30',
#         '11:45',
#         '12:00',
#         '12:15',
#         '12:30',
#         '12:45',
#         '13:00',
#         '13:15',
#         '13:30',
#         '13:45',
#         '14:00',
#         '14:15',
#         '14:30',
#         '14:45',
#         '15:00',
#         '15:15',
#         '15:30',
#      ] 

#     livePrice = api_data['records']['underlyingValue']
#     base_zone_obj = BaseZoneBanknifty.objects.all().values() 
#     if len(base_zone_obj) != 0:
#         if base_zone_obj[0]['in_basezone'] == True:
#             if current_time in times:
#                 LiveDataBankNifty.objects.create(live_price = livePrice, in_basezone=True)
#                 print("LiveData Added successfully", livePrice)
        
#     else:
#         if current_time in times:
#             LiveDataBankNifty.objects.create(live_price = livePrice)
#             print(current_time in times)
#             print("LiveData Added successfully", livePrice)