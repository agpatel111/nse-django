from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .serializers import *
import datetime
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
import requests
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta


# Create your views here.

def home(request):
    data = stock_detail.objects.all().order_by("-buy_time").values()
    dataa = []
    for i in data:
        BuyTime = i['buy_time']
        BuyTimeFormt = datetime.date(BuyTime)
        today = date.today()
        if BuyTimeFormt == today:
            i['today'] = 'True'
        dataa.append(i)
    return render(request, "base.html", {"data": dataa})

def settings(request):
    data = live.objects.all()
    return render(request, 'settings.html', { 'data' : data })

@csrf_exempt
def changesettings(request):
    if request.method == 'POST':
        name = request.POST['name'] 
        obj = request.POST['live']
        if obj == 'True':
            obj = False
        else:
            obj = True
        if name == 'BankNifty':
            live.objects.filter(id = 1).update(live_banknifty = obj)
            return JsonResponse({'status' : 1})
        if name == 'Nifty':
            live.objects.filter(id = 1).update(live_nifty = obj)
            return JsonResponse({'status' : 1})

@api_view(['POST'])
def stock(request):
    try:
        if request.data['name'] == '':
            return Response({ 'status': False, 'msg': 'name Required'}) 
        name = request.data['name']

        baseurl = "https://www.nseindia.com/"
        headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) '
                            'Chrome/80.0.3987.149 Safari/537.36',
            'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
        session = requests.Session()
        req = session.get(baseurl, headers=headers, timeout=5)
        cookies = dict(req.cookies)
        url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + name

        response = requests.get(url, headers=headers, timeout=5, cookies=cookies)
        data = response.text
        api_data = json.loads(data)

        timestamp = api_data['records']['timestamp']
        livePrice = api_data['records']['underlyingValue']

        down_price = []    # upside from blue colour
        down__price = api_data['filtered']['data']
        for down in down__price:
            if down['strikePrice'] <= livePrice:
                down_price.append(down) 

        up_price = []     # down side from blue colour
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
        downSliceList = downSliceList[:1]   #PE red Colour

        upSliceList = []
        for upSlice in up_price[0:5]:
            ss = upSlice['CE']['openInterest'] + upSlice['CE']['changeinOpenInterest']
            upSliceList.append(ss)
        upSliceList.sort()
        upSliceList.reverse()
        upSliceList = upSliceList[:1]       #CE red Colour

        PEMax = []
        PEMaxValue = []                 #PE red Colour Strike Price
        for downn in down_price[:-6:-1]:
            aaa = downn['PE']['changeinOpenInterest'] + downn['PE']['openInterest']
            if aaa == downSliceList[0]:
                PEMax.append(downn)
                PEMaxValue.append(downn['strikePrice'])

        CEMax = []
        CEMaxValue = []                 #CE red Colour Strike Price
        for upp in up_price[0:5]:
            upppp = upp['CE']['changeinOpenInterest'] + upp['CE']['openInterest']
            if upppp == upSliceList[0]:
                CEMax.append(upp)
                CEMaxValue.append(upp['strikePrice'])

        summ = api_data['filtered']['CE']['totOI']
        summ2 = api_data['filtered']['PE']['totOI']
        pcr = summ2 / summ

        data = [{ 'name': name , 'timestamp': timestamp,'pcr': pcr, 'livePrice': livePrice,'PEMax': PEMax,'CEMax': CEMax, 'down_price': down_price, 'up_price': up_price }]
        return Response({ 'status' : True, 'data': data })
    except Exception as e:
        print('stock->', name, e)
        return Response({ 'status' : False, 'message': 'Something is wrong' })


def pcr(request):
    stock_url = 'https://zerodha.harmistechnology.com/stockname'
    stock_responce = requests.get(stock_url)
    stock_data = stock_responce.text
    stock_api_data = json.loads(stock_data)
    stocks = []
    for i in stock_api_data['data']:
        stocks.append(i['name'])
    # print(stocks)

    update_needed = []
    success_count = 0
    reject_count = 0

    baseurl = "https://www.nseindia.com/"
    headers =  {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                         'like Gecko) '
                         'Chrome/80.0.3987.149 Safari/537.36',
           'accept-language': 'en,gu;q=0.9,hi;q=0.8', 'accept-encoding': 'gzip, deflate, br'}
    session = requests.Session()
    req = session.get(baseurl, headers=headers, timeout=5)
    cookies = dict(req.cookies)
    for stock in stocks:
        url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock
        try:
            response = requests.get(url, headers=headers, timeout=5, cookies=cookies)
            data = response.text
            api_data = json.loads(data)

            livePrice = api_data['records']['underlyingValue']

            sum = api_data['filtered']['CE']['totOI']
            sum2 = api_data['filtered']['PE']['totOI']
            pcr = '%.2f'% (sum2 / sum)

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

            diff = downSliceList[0] - upSliceList[0]
            if diff > 0:
                pe_ce_Diff = True
            else:
                pe_ce_Diff = False

            payload = {'name': stock, 'pcr': pcr, 'PE_CE_diffrent': pe_ce_Diff}
            r = requests.put(
                "https://zerodha.harmistechnology.com/stockname", data=payload)
            success_count = success_count + 1
            # pcr_stock_name.objects.filter(name = stock).update(pcr =  pcr)
            print(stock, '->',pcr, '->', pe_ce_Diff)
            
        except Exception as e:
            print('Error-->',e)
            print('An exception occurred','->', stock)
            update_needed.append(stock)
            reject_count = reject_count + 1
    return render(request, "PcrStock.html", { 'update_needed' : update_needed, 'success_count' : success_count, 'reject_count': reject_count })

class stock_details(APIView):
    # permission_classes = [IsAuthenticated]              
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        nse_objs = stock_detail.objects.all()
        # demo = stock_detail.objects.values_list().values()
        serializer = stockListSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "stock details fetched", "data": serializer.data}
        )

    def post(self, request):
        try:
            data = request.data
            # _mutable = data._mutable
            # data._mutable = True
            print(data)
            serializer = stockPostSerializer(data=data)
            data["status"] = "BUY"
            # print(data["status"])
            # data["sell_buy_time"] = "-"
            # data._mutable = _mutable
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "msg": "Successfully BUY Stock", "data": serializer.data}
                )
            else:
                return Response(
                    {"status": False, "msg": "invalid data", "data": serializer.errors}
                )

        except Exception as e:
            print(e)
        return Response(
            {
                "status": False,
                "msg": "Somthing Went Wrong",
            }
        )

    def put(self, request):
        try:
            data = request.data
            if not data.get("id"):
                return Response({"status": False, "msg": "id is required", "data": {}})

            obj = stock_detail.objects.get(id=data.get("id"))
            serializer = stockPostSerializer(obj, data=data, partial=True)
            if ('exit_price' in data):
                data["status"] = "SELL"
                data["sell_buy_time"] = datetime.datetime.today()
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "msg": "Successfully SELL Stock",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "msg": "invalid data",
                        "data": serializer.errors,
                    }
                )
        except Exception as e:
            print(e)
            return Response({"status": False, "msg": "Invalid id", "data": {}})


# <-------------------------------- setting ---------------------------------->

class setting_nse(APIView):
    # permission_classes = [IsAuthenticated]              
    # authentication_classes = [TokenAuthentication]
    
    def get(self, request):
        nse_objs = nse_setting.objects.all()
        serializer = settingSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "settings fetched", "data": serializer.data}
        )

    def post(self, request):

        try:
            data = request.data
            # _mutable = data._mutable
            # data._mutable = True
            serializer = settingSerializer(data=data)
           
    
            # data["sell_buy_time"] = "-"
            # data._mutable = _mutable
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "msg": "success data", "data": serializer.data}
                )
            else:
                return Response(
                    {"status": False, "msg": "invalid data", "data": serializer.errors}
                )

        except Exception as e:
            print(e)
        return Response(
            {
                "status": False,
                "msg": "Somthing Went Wrong",
            }
        )

    def put(self, request):
        try:
            data = request.data
            if not data.get("id"):
                return Response({"status": False, "msg": "id is required", "data": {}})

            obj = nse_setting.objects.get(id=data.get("id"))
            serializer = settingSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "msg": "success data anand",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "msg": "invalid data anand",
                        "data": serializer.errors,
                    }
                )
        except Exception as e:
            print(e)
            return Response({"status": False, "msg": "Invalid id", "data": {}})

    def delete(self, request):
        try:
            data = request.data
            if not data.get('id'):
                return Response({
                'status' : False,
                'msg' : 'Id is required', 
                'data' : {}
            }) 
            obj = nse_setting.objects.get(id= data.get('id'))
            if request.method == "DELETE":
                obj.delete()
                return Response({
                'status' : True,
                'msg' : 'successfully deleted data',
            })
            else:
                return Response({
                    'status' : False,
                    'msg' : 'Provide Delete method', 
                })
        except Exception as e:
            print(e)
        return Response({
                'status': False,
                'msg': 'Invalid Id',
                'data' : {} 
            })            



@api_view(['PUT'])
def patch_stock(request,pk):

    try:
        data = request.data
        obj = nse_setting.objects.get(id= pk)
        serializer = settingSerializer(obj, data = data, partial = True)
        print("hello")
        if serializer.is_valid():
            serializer.save()
            return Response({ 'status' : True, 'msg' : 'success data', 'data' : serializer.data })
        else:
            return Response({ 'status' : False, 'msg' : 'invalid data', 'data' : serializer.errors })
    except Exception as e:
        print(e)
        return Response({ 'status': False, 'msg': 'Invalid uid', 'data' : {} })        

@api_view(['DELETE'])
def delete_stock(request, pk):
    try:
        obj = nse_setting.objects.get(id = pk)
        obj.delete()
        return Response({ 'status' : True, 'msg' : 'success DELETE data' })
    except Exception as e:
            print(e)
            return Response({ 'status': False, 'msg': 'Invalid uid', 'data' : {} })


@api_view(['GET'])
def get_nse_data(self , request , pk):
       if request.method == 'GET':
        snippets = nse_setting.objects.get(id = pk)
        serializer = settingSerializer(snippets, many=True)
        return Response(serializer.data)
        # nse_objs = nse_setting.objects.all( id = pk)
        # serializer = settingSerializer(nse_objs, many=True)
        # return Response(
        #     {"status": True, "msg": "nse_profit fetched", "data": serializer.data}

class SnippetDetail(APIView):

    def get_object(self, pk):
        try:
            return nse_setting.objects.get(pk=pk)
        except nse_setting.DoesNotExist:
            raise "Http404"

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = settingSerializer(snippet)
        return Response(serializer.data)        


class Logout(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, format=None):
        # simply delete the token to force a login
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class PcrStockName(APIView):
    # permission_classes = [IsAuthenticated]              
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        nse_objs = pcr_stock_name.objects.all()
        serializer = pcr_stock_nameSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "Stock Details Fetched", "data": serializer.data}
        )

    def post(self, request):

        try:
            data = request.data
            serializer = pcr_stock_nameSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "msg": "Successfully Post Data", "data": serializer.data}
                )
            else:
                return Response(
                    {"status": False, "msg": "invalid data", "data": serializer.errors}
                )

        except Exception as e:
            print(e)
        return Response(
            {
                "status": False,
                "msg": "Somthing Went Wrong",
            }
        )

    def put(self, request):
        try:
            data = request.data
            print(data)
            if not data.get("name"):
                return Response({"status": False, "msg": "name is required", "data": {}})

            obj = pcr_stock_name.objects.get(name=data.get("name"))
            print(obj)
            serializer = pcr_stock_nameSerializer(obj, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "msg": "successfully Update Stock Data",
                        "data": serializer.data,
                    }
                )
            else:
                return Response(
                    {
                        "status": False,
                        "msg": "invalid data",
                        "data": serializer.errors,
                    }
                ) 
        except Exception as e:
            print(e)
            return Response({"status": False, "msg": "Invalid StockName", "data": {}})


import requests
import requests
import json


def print_hello(request):
    # print("HELLLLLO")
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    headers = {'user-agent': 'my-app/0.0.1'}
    response = requests.get(url, headers=headers)
    data = response.json()
    timestamp = data['records']
    # print(data)
    return JsonResponse({"timestamp": timestamp })