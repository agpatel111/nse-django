from datetime import date, datetime
from rich.console import Console

consoleGreen = Console(style='green')



class Coustom():
    def downPrice(data, livePrice):
        down_price = []
        for down in data:
            if down['strikePrice'] <= livePrice:
                down_price.append(down)
        return down_price

    def upPrice(data, livePrice):
        up_price = []
        for up in data:
            if up['strikePrice'] >= livePrice:
                up_price.append(up) 
        return up_price

    def downMaxValue(data):
        downSliceList = []
        for downSlice in data:
            var = downSlice['PE']['openInterest'] + downSlice['PE']['changeinOpenInterest']
            downSliceList.append(var)
        downSliceList.sort()
        downSliceList.reverse()
        downSliceList = downSliceList[:1]

        return downSliceList
    
    def upMaxValue(data):
        upSliceList = []
        for upSlice in data:
            var = upSlice['CE']['openInterest'] + upSlice['CE']['changeinOpenInterest']
            upSliceList.append(var)
        upSliceList.sort()
        upSliceList.reverse()
        upSliceList = upSliceList[:1]
        
        return upSliceList
    
    def basePriceData(down_price, downSliceList ):
        PEMax = []
        PEMaxValue = []
        for down in down_price:
            var = down['PE']['changeinOpenInterest'] + down['PE']['openInterest']
            if var == downSliceList[0]:
                PEMax.append(down)
                PEMaxValue.append(down['strikePrice'])
        
        return PEMax, PEMaxValue
    
    def resistancePriceData(up_price, upSliceList):
        CEMax = []
        CEMaxValue = []
        for up in up_price:
            var = up['CE']['changeinOpenInterest'] + up['CE']['openInterest']
            if var == upSliceList[0]:
                CEMax.append(up)
                CEMaxValue.append(up['strikePrice'])
        
        return CEMax, CEMaxValue

    def pcrValue(api_data):
        summ = api_data['filtered']['CE']['totOI']
        summ2 = api_data['filtered']['PE']['totOI']
        pcr = summ2 / summ
        pcr = '%.2f'%(pcr)
        pcr = float(pcr)
        return pcr
    
    def buyCondition(stock_details, OptionId, call_put):
        for i in stock_details:
            if i['percentage_id'] == OptionId and i['status'] == 'BUY' and i['call_put'] == call_put :
                setBuyCondition = False
                break
            else:
                setBuyCondition = True
        
        return setBuyCondition
    
    def buyCondition_withOneStock(stock_details, OptionId, call_put, option):
        profit = 0
        loss = 0
        for i in stock_details:
            if i['percentage_id'] == OptionId and i['status'] == 'BUY' and i['call_put'] == call_put :
                setBuyCondition = False
                break
            else:
                setBuyCondition = True

            buy_time = i['buy_time']
            buyy_date = datetime.date(buy_time)
            today = date.today()
            if buyy_date == today and i['percentage_id'] == OptionId:
                if i['final_status'] == "PROFIT":
                    profit = profit + 1
                elif i['final_status'] == "LOSS":
                    loss = loss + 1
        if profit > loss:
            setOneStock = False
            consoleGreen.print(f"YOU MAKE PROFIT TODAY IN {option} {call_put}")
        else:
            setOneStock = True
            
        return setBuyCondition, setOneStock