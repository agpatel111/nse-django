import pandas as pd
import pyotp
import os
from SmartApi import SmartConnect
from datetime import date, datetime
import requests
from nse_app.models import *

def angleDetails():
    data = {
        'username': 'H117838',
        'apikey': 'SqtdCpAg',
        'password': '4689',
        't_otp': 'K7QDKSEXWD7KRO7EVQCUHTFK2U'
    }
    # url = 'http://zerodha.harmistechnology.com/accountDetail'
    # response = requests.get(url).json()
    # data = response[0]
    return data['username'], data['apikey'], data['password'], data['t_otp']


def getTokenApiData():
    def fetch_and_store_data():
        url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
        try:
            d = requests.get(url).json()
            token_df = pd.DataFrame.from_dict(d)
            token_df['expiry'] = pd.to_datetime(token_df['expiry'])
            token_df = token_df.astype({'strike': float})

            df = pd.DataFrame(token_df)
            df.to_csv('data.csv', index=False)
            # print(f'Data saved to data.csv on {datetime.now()}')
        except Exception as e:
            print(f'Error fetching or saving data: {str(e)}')

    if not os.path.exists('data.csv'):
        fetch_and_store_data()
        token_df = pd.read_csv('data.csv', low_memory=False)
    else:
        last_modified_time = datetime.fromtimestamp(os.path.getmtime('data.csv'))

        if last_modified_time.date() != datetime.now().date():
            fetch_and_store_data()
            token_df = pd.read_csv('data.csv', low_memory=False)
        else:
            token_df = pd.read_csv('data.csv', low_memory=False)
    return token_df


def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):

    df = getTokenApiData()
    strike_price = strike_price*100
    
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE')]
        return eq_df[eq_df['name'] == symbol]

    ## OPTION STRIKE PRICE
    elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
        return df[(df['exch_seg'] == 'NFO') & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])

    ## OPTION FUTURE
    elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['symbol'].str.endswith('FUT'))].sort_values(by=['expiry'])

    # elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
    #     return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])


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
    obj.generateSession(username, pwd, totp)
    
    # Expiry Date
    expiry_date = exprityDate

    def place_order_carryforward(token, symbol, qty,exch_seg ,buy_sell,ordertype ,price, variety='ROBO', triggerprice=5):
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
            # # orderId = obj.placeOrder(orderparams)
            # # orderId = 0zt(orderId))
            # stock_detail.objects.filter(id = id).update(order_id = orderId, qty = total_qty)

        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))                   

    def place_order_bo(token, symbol, qty, buy_sell, ordertype, price, variety='ROBO', exch_seg='NFO', triggerprice=5):
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
            # orderId = obj.placeOrder(orderparams)
            # print("The order id is: {}".format(orderId))

        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))

    
    # def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):
    #     url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    #     d = requests.get(url).json()
    #     token_df = pd.DataFrame.from_dict(d)
    #     token_df['expiry'] = pd.to_datetime(
    #         token_df['expiry']).apply(lambda x: x.date())
    #     token_df = token_df.astype({'strike': float})

    #     df = token_df
    #     strike_price = strike_price*100
    #     if exch_seg == 'NSE':
    #         eq_df = df[(df['exch_seg'] == 'NSE')]
    #         return eq_df[eq_df['name'] == symbol]
    #     elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
    #         return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
    #     elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
    #         return df[(df['exch_seg'] == 'NFO') & (df['expiry'] == expiry_day) & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])


    ## banknifty PUT
    if percentions_sm == 3:
        symbol = 'BANKNIFTY'
        token_data = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', expiry_date).iloc[0]
        place_order_bo(token_data['token'], token_data['symbol'], token_data['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')

    ## banknifty CALL
    elif percentions_sm == 1:
        symbol = 'BANKNIFTY'

        token_data = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', expiry_date).iloc[0]
        place_order_bo(token_data['token'], token_data['symbol'], token_data['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')

    ## nifty PUT
    elif percentions_sm == 4:
        symbol = 'NIFTY'
        token_data = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'PE', expiry_date).iloc[0]
        place_order_bo(token_data['token'], token_data['symbol'], token_data['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')

    ## nifty CALL
    elif percentions_sm == 2:
        symbol = 'NIFTY'
        token_data = getTokenInfo(symbol, 'NFO', 'OPTIDX', base_strike_price_sm, 'CE', expiry_date).iloc[0]
        place_order_bo(token_data['token'], token_data['symbol'], token_data['lotsize'], 'BUY', 'MARKET', 0, 'NORMAL', 'NFO')



def sellFunStock(strikePrice, BidPrice, squareoff, stoploss, OptionId, lots, stockName):

    base_strike_price_sm = float(strikePrice)
    buy_price_sm = str(BidPrice)
    squareoff_sm = squareoff
    stoploss_sm = stoploss
    percentions_sm = OptionId
    lot_size = lots
    
    username, apikey, password, t_otp = angleDetails()

    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    obj = SmartConnect(api_key=apikey)
    dataa = obj.generateSession(username, pwd, totp)

    
    def place_order_carryforward(token, symbol, qty, exch_seg, buy_sell, ordertype, price, variety='ROBO', triggerprice=5):
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
            # orderId = obj.placeOrder(orderparams)
            # print("The order id is: {}".format(orderId))
            # stock_detail.objects.filter(id = get_id).update(orderid = orderId)
        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))   
    
    
    def place_order_bo(token, symbol, qty, buy_sell, ordertype, price, variety='ROBO', exch_seg='NFO', triggerprice=5):
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
            # orderId = obj.placeOrder(orderparams)
            # print("The order id is: {}".format(orderId))

        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))

    
    # url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    # d = requests.get(url).json()
    # token_df = pd.DataFrame.from_dict(d)
    # token_df['expiry'] = pd.to_datetime(
    #     token_df['expiry']).apply(lambda x: x.date())
    # token_df = token_df.astype({'strike': float})

    # def getTokenInfo(symbol, exch_seg='NSE', instrumenttype='OPTIDX', strike_price='', pe_ce='CE', expiry_day=None):
    #     df = token_df
    #     strike_price = strike_price*100
    #     if exch_seg == 'NSE':
    #         eq_df = df[(df['exch_seg'] == 'NSE')]
    #         return eq_df[eq_df['name'] == symbol]
    #     elif exch_seg == 'NFO' and ((instrumenttype == 'FUTSTK') or (instrumenttype == 'FUTIDX')):
    #         return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol)].sort_values(by=['expiry'])
    #     elif exch_seg == 'NFO' and (instrumenttype == 'OPTSTK' or instrumenttype == 'OPTIDX'):
    #         return df[(df['exch_seg'] == 'NFO') & (df['expiry'] == expiry_day) & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & (df['symbol'].str.endswith(pe_ce))].sort_values(by=['expiry'])

    exprityDateStock = date(2023, 4, 27)
        
    if percentions_sm == 5: 
        symbol = stockName
        token_data = getTokenInfo(symbol,'NFO','OPTSTK', base_strike_price_sm,'CE', exprityDateStock).iloc[0]
        place_order_carryforward(token_data['token'],token_data['symbol'],token_data['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')

    if percentions_sm == 7: 
        symbol = stockName
        token_data = getTokenInfo(symbol,'NFO','OPTSTK', base_strike_price_sm,'PE', exprityDateStock).iloc[0]
        place_order_carryforward(token_data['token'],token_data['symbol'],token_data['lotsize'],'SELL','MARKET',0,'NORMAL','NFO')



def optionFuture(option, lots, profit, loss, buy_sell='BUY'):
    '''
    Buy Index Future
    '''
    f_token = getTokenInfo(option ,'NFO', 'FUTIDX', '', '').iloc[0]
    symbol = f_token['symbol']
    token = f_token['token']
    lot = f_token['lotsize']

    username, apikey, password, t_otp = angleDetails()

    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    obj = SmartConnect(api_key=apikey)
    obj.generateSession(username, pwd, totp)

    ltp = obj.ltpData('NFO', symbol, token)
    ltp = ltp['data']['ltp']
    
    if buy_sell == 'BUY':
        squareoff = ltp + profit
        stoploss = ltp - loss
    else:
        squareoff = ltp - profit
        stoploss = ltp + loss
        
    def place_order_bo(token, symbol, qty, exch_seg, buy_sell, ordertype, price):
        qty = int(qty) * lots
        
        try:
            orderparams = {
                "variety": 'ROBO',
                "tradingsymbol": symbol,
                "symboltoken": token,
                "transactiontype": buy_sell,
                'exchange': exch_seg,
                "ordertype": ordertype,
                "producttype": 'BO',
                "duration": "DAY",
                "price": price,
                "squareoff": squareoff,
                "stoploss": stoploss,
                "quantity": qty,
            }
            
            # orderId = obj.placeOrder(orderparams)
            print(orderparams)
            return {'orderId': ltp, 'ltp':ltp, "squareoff": squareoff, "stoploss": stoploss}
            # return orderId
            
        except Exception as e:
            print(
                "Order placement failed: {}".format(e.message))
    
    return place_order_bo(token, symbol, lot, 'NFO', buy_sell, 'LIMIT', ltp)


def futureLivePrice(option):
    '''
    future live price of index
    '''
    f_token = getTokenInfo(option ,'NFO', 'FUTIDX', '', '').iloc[0]
    symbol = f_token['symbol']
    token = f_token['token']

    username, apikey, password, t_otp = angleDetails()

    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    obj = SmartConnect(api_key=apikey)
    obj.generateSession(username, pwd, totp)

    ltp = obj.ltpData('NFO', symbol, token)
    return ltp['data']['ltp']

def futureStockLivePrice(stock):
    '''
    future live price of index
    '''
    f_token = getTokenInfo(stock ,'NFO', 'FUTSTK', '', '').iloc[0]
    symbol = f_token['symbol']
    token = f_token['token']

    username, apikey, password, t_otp = angleDetails()

    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    obj = SmartConnect(api_key=apikey)
    obj.generateSession(username, pwd, totp)

    ltp = obj.ltpData('NFO', symbol, token)
    return ltp['data']['ltp']


def stockFutureBuyPrice(stock, lots, profit, loss, buy_sell='BUY'):
    '''
    stock Future live price of index
    '''
    f_token = getTokenInfo(stock ,'NFO', 'FUTSTK', '', '').iloc[0]
    symbol = f_token['symbol']
    token = f_token['token']
    qty = f_token['lotsize']
    username, apikey, password, t_otp = angleDetails()

    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    obj = SmartConnect(api_key=apikey)
    obj.generateSession(username, pwd, totp)
    ltp = obj.ltpData('NFO', symbol, token)
    ltp = ltp['data']['ltp']
    
    profit = (ltp * profit) / 100
    loss = (ltp * loss) / 100
    
    if buy_sell == 'BUY':
        squareoff = ltp + profit
        stoploss = ltp - loss
    else:
        squareoff = ltp - profit
        stoploss = ltp + loss

    orderId = 0
    return ltp, round(squareoff, 2), round(stoploss, 2), orderId, qty*int(lots)


def ltpData(option_name, strikePrice, pe_ce, a):
    '''
    live price of option strike price
    '''
    token_info = getTokenInfo(option_name, 'NFO', 'OPTIDX', strikePrice, pe_ce, a).iloc[0]
    symbol = token_info['symbol']
    token = token_info['token']
    lot = token_info['lotsize']
    
    username, apikey, password, t_otp = angleDetails()
    
    username = username
    apikey = apikey
    pwd = password
    totp = pyotp.TOTP(t_otp).now()
    smartapi = SmartConnect(api_key=apikey)
    smartapi.generateSession(username, pwd, totp)

    ltp = smartapi.ltpData('NFO', symbol, token )
    ltp = ltp['data']['ltp']
    return ltp
