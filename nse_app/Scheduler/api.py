
import pyotp
from smartapi import SmartConnect
import pandas as pd
import requests
from datetime import date

def sellFun():
    # print("DATAAAAA--------->", strikePrice, BidPrice, squareoff, stoploss, OptionId)
    base_strike_price_sm = float(43000)
    buy_price_sm = str(406.25)
    squareoff_sm = str(81.25)
    stoploss_sm = str(40.62)
    percentions_sm = 1
    lot_size = 2.0
    # squareoff = data['sell_price']
    # stoploss = data['stop_loseprice']
    print(buy_price_sm,squareoff_sm, base_strike_price_sm , stoploss_sm, percentions_sm)

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

    def place_order(token, symbol, qty, buy_sell, ordertype, price, variety='ROBO', exch_seg='NFO', triggerprice=stoploss_sm):
        print(qty)
        total_lot = float(qty) * lot_size
        total_lot = int(total_lot)
        total_lot = str(total_lot)
        print(total_lot)
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
                "quantity": qty,
                "trailingStopLoss": "5",
            }
            print(orderparams)
            # orderId = obj.placeOrder(orderparams)
            # print("The order id is: {}".format(orderId))

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

    a = date(2023, 1, 5)

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

        # print("NIFTY ce", ce_strike_symbol)
    

sellFun()