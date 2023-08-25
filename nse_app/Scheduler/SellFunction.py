import pandas as pd
import pyotp
from SmartApi import SmartConnect
from datetime import date
import requests
from nse_app.models import *




def sellFunOption(strikePrice, BidPrice, squareoff, stoploss, OptionId, lots, id, exprityDate):
   
    base_strike_price_sm = float(strikePrice)
    buy_price_sm = str(BidPrice)
    squareoff_sm = squareoff
    stoploss_sm = stoploss
    percentions_sm = OptionId
    lot_size = lots
    
    
    obj = AccountCredential.objects.all().values().last()
    username = obj['username']
    apikey = obj['apikey']
    password = obj['password']
    t_otp = obj['t_otp']

    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    obj = SmartConnect(api_key=apikey)
    dataa = obj.generateSession(username, pwd, totp)
    
    
    # Expiry Date
    expiry_date = exprityDate

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
            # orderId = obj.placeOrder(orderparams)
            orderId = 0
            print("The order id is: {}".format(orderId))
            stock_detail.objects.filter(id = id).update(order_id = orderId, qty = total_qty)

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

    
    def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):
        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        d = requests.get(url).json()
        token_df = pd.DataFrame.from_dict(d)
        token_df['expiry'] = pd.to_datetime(
            token_df['expiry']).apply(lambda x: x.date())
        token_df = token_df.astype({'strike': float})

        df = token_df
        strike_price = strike_price*100
        if exch_seg == 'NSE':
            eq_df = df[(df['exch_seg'] == 'NSE')]
            return eq_df[eq_df['name'] == symbol]
        elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
            return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
        elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
            return df[(df['exch_seg'] == 'NFO') & (df['expiry'] == expiry_day) & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])


    ## banknifty put
    if percentions_sm == 3:
        symbol = 'BANKNIFTY'
        pe_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', expiry_date).iloc[0]
        place_order(pe_strike_symbol['token'], pe_strike_symbol['symbol'],
                    pe_strike_symbol['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')

    ## banknifty call
    elif percentions_sm == 1:
        symbol = 'BANKNIFTY'

        ce_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', expiry_date).iloc[0]
        place_order(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

    ## nifty put
    elif percentions_sm == 4:
        symbol = 'NIFTY'
        qty = 25
        pe_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', expiry_date).iloc[0]
        place_order(pe_strike_symbol['token'], pe_strike_symbol['symbol'],
                    pe_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO', qty)

    ## nifty call
    elif percentions_sm == 2:
        symbol = 'NIFTY'
        ce_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', expiry_date).iloc[0]
        place_order(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

    ## banknifty call pcr
    elif percentions_sm == 6:
        symbol = 'BANKNIFTY'
        ce_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', expiry_date).iloc[0]
        place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

    ## banknifty put pcr
    elif percentions_sm == 9:
        symbol = 'BANKNIFTY'
        ce_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', expiry_date).iloc[0]
        place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')
        
    ## nifty call pcr
    elif percentions_sm == 8:
        symbol = 'NIFTY'
        ce_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', expiry_date).iloc[0]
        place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')

    ## nifty put pcr
    elif percentions_sm == 10:
        symbol = 'NIFTY'
        ce_strike_symbol = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', expiry_date).iloc[0]
        place_order_pcr(ce_strike_symbol['token'], ce_strike_symbol['symbol'],
                    ce_strike_symbol['lotsize'], 'SELL', 'MARKET', 0, 'NORMAL', 'NFO')
        
        
        

def sellFunStock(strikePrice, BidPrice, squareoff, stoploss, OptionId, lots, stockName):
   
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

    
    def place_order_pcr(token, symbol, qty, exch_seg, buy_sell, ordertype, price, variety='ROBO', triggerprice=5):
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
                "ordertype": 'MARKET',
                "producttype": 'CARRYFORWARD',
                "duration": "DAY",
                "price": '0',    
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

    exprityDateStock = date(2023, 4, 27)
        
    if percentions_sm == 5: 
        symbol = stockName
        print("stock_name_nse",stockName, base_strike_price_sm, exprityDateStock)
        ce_strike_symbol = getTokenInfo(symbol,'NFO','OPTSTK', base_strike_price_sm,'CE', exprityDateStock).iloc[0]
        place_order_pcr(ce_strike_symbol['token'],ce_strike_symbol['symbol'],ce_strike_symbol['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')
        print("stock pe", ce_strike_symbol)  

    if percentions_sm == 7: 
        symbol = stockName
        print("stock_name_nse",stockName, base_strike_price_sm, exprityDateStock)
        ce_strike_symbol = getTokenInfo(symbol,'NFO','OPTSTK', base_strike_price_sm,'PE', exprityDateStock).iloc[0]
        place_order_pcr(ce_strike_symbol['token'],ce_strike_symbol['symbol'],ce_strike_symbol['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')
        print("stock pe", ce_strike_symbol)   



def getTokenInfoFuture(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):

    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike': float})

    df = token_df
    strike_price = strike_price*100

    ## OPTION FUTURE
    if exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['symbol'].str.endswith('FUT'))].sort_values(by=['expiry'])
        

def optionFuture(option, lots):
    f_token = getTokenInfoFuture(option ,'NFO', 'FUTIDX', '', '').iloc[0]
    symbol = f_token['symbol']
    token = f_token['token']
    lot = f_token['lotsize']

    username = 'H117838'
    apikey = 'SqtdCpAg'
    pwd = '4689'
    totp = pyotp.TOTP('K7QDKSEXWD7KRO7EVQCUHTFK2U').now()
    obj = SmartConnect(api_key=apikey)
    obj.generateSession(username, pwd, totp)

    ltp = obj.ltpData('NFO', symbol, token)
    
    def place_order(token, symbol, qty, exch_seg, buy_sell, ordertype, price):
        qty = int(qty) * lots
        # qty = int(qty) * 20
        qty = str(qty)
        try:
            orderparams = {
                "variety": 'NORMAL',
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": buy_sell,
                'exchange': exch_seg,
                "ordertype": ordertype,
                "producttype": 'CARRYFORWARD',
                "duration": "DAY",
                "price": price,
                "squareoff": "0",
                "stoploss": "0",
                "quantity": qty,
            }
            print(ltp)
            return ltp['data']['ltp']
            # orderId = obj.placeOrder(orderparams)
            # print(orderId)
            
        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))
    
    return place_order(token, symbol, lot, 'NFO', 'BUY', 'MARKET', 0)