from .models import *
from .serializers import *
from django.shortcuts import render, redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
import datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
import requests
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import date, datetime
from nse_app.services import StockView
from nse_app.Scheduler.CoustomFun import Coustom
from django.core.paginator import Paginator
from django.utils import timezone


def home(request):
    data = stock_detail.objects.all().order_by("-buy_time").values()
    paginator = Paginator(data, 25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    today = date.today()
    # for i in page.object_list:
    #     BuyTime = i['buy_time']
    #     BuyTimeFormt = datetime.date(BuyTime)
    #     if BuyTimeFormt == today:
    #         i['today'] = 'True'

        
    pagination_info = {
    'page': page,
    'paginator': paginator,
    }
    return render(request, "tailwind/Home.html", {"data": page.object_list, 'pagination_info': pagination_info, 'today': today})


def deleteStock(request, id):
    stock =  stock_detail.objects.get(id = id)
    stock.delete()
    return redirect("nse_app:home")


def PcrValue(request):
    today = date.today()
    today = timezone.make_aware(timezone.datetime(today.year, today.month, today.day))
    data = pcr_values.objects.filter(timestamp__gte = today).order_by("-timestamp")
    # arr1 = []
    # for i in data:
    #     BuyTimeFormt = datetime.date(i['timestamp'])
    #     if BuyTimeFormt == today:
    #         arr1.append(i)
    return render(request, 'tailwind/PcrValues.html', {'data': data})

def settings(request):
    data = live.objects.all()
    return render(request, 'tailwind/settings.html', { 'data' : data })

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
            return JsonResponse({'status' : 1, 'data': obj})
        if name == 'Nifty':
            live.objects.filter(id = 1).update(live_nifty = obj)
            return JsonResponse({'status' : 1, 'data': obj})
        if name == 'StockCe':
            live.objects.filter(id = 1).update(live_stock_ce = obj)
            return JsonResponse({'status' : 1, 'data': obj})
        if name == 'StockPe':
            live.objects.filter(id = 1).update(live_stock_pe = obj)
            return JsonResponse({'status' : 1, 'data': obj})

@api_view(['POST'])
def stockData(request):
    try:
        if request.data['name'] == '':
            return Response({ 'status': False, 'msg': 'name Required'}) 
        name = request.data['name']
       
        # {% Call custom Fun to Fetch Data %}
        data = StockView.StockviewFun(name)
        data = [ data ]
               
        return Response({ 'status' : True, 'data': data })
    except Exception as e:
        print('stock->', name, e)
        return Response({ 'status' : False, 'message': 'Something is wrong' })

@api_view(['GET'])
def getStock(request, slug):
    name = slug
    try:
       
        # {% Call custom Fun to Fetch Data %}
        data = StockView.StockviewFun(name)
        data = [ data ]
               
        return JsonResponse({ 'status' : True, 'data': data })
    except Exception as e:
        print('stock->', name, e)
        return Response({ 'status' : False, 'message': 'Something is wrong' })

def pcrUpdate(request):
    stock_url = 'https://zerodha.harmistechnology.com/stockname'
    stock_responce = requests.get(stock_url)
    stock_data = stock_responce.text
    stock_api_data = json.loads(stock_data)
    dataaaa = stock_for_buy.objects.filter(call_or_put='CALL').values()

    stocks = []
    for i in stock_api_data['data']:
        stocks.append(i['name'])
        
    stock_for_buy.objects.all().delete()
    
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

    call_defs = []
    put_defs = []
    for stock in stocks:
        extra_setting.objects.filter(id = 1).update(pcr_isupdating = True)

        url = 'https://www.nseindia.com/api/option-chain-equities?symbol=' + stock
        try:
            response = requests.get(url, headers=headers, timeout=5, cookies=cookies)
            data = response.text
            api_data = json.loads(data)

            livePrice = api_data['records']['underlyingValue']
            filteredData = api_data['filtered']['data']

            pcr = Coustom.pcrValue(api_data)
            down_price = Coustom.downPrice(filteredData, livePrice)
            up_price = Coustom.upPrice(filteredData, livePrice)
            downSliceList = Coustom.downMaxValue(down_price[:-6:-1])
            upSliceList = Coustom.upMaxValue(up_price[0:5])
            PEMax, PEMaxValue = Coustom.basePriceData(down_price[:-6:-1], downSliceList)
            CEMax, CEMaxValue = Coustom.resistancePriceData(up_price[0:5], upSliceList)
            
            ## Down Side
            CE__fist_down = down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest']
            PE__fist_down = down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']
            PE_side_persnt = float('%.2f'% ((CE__fist_down / PE__fist_down) * 100))

            ## Up side
            CE__fist_Up = up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest']
            PE__fist_Up = up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']
            CE_side_persnt = float('%.2f'% ((PE__fist_Up / CE__fist_Up) * 100))
            
            
            ### CALLL
            if down_price[-1]['strikePrice'] == PEMaxValue[0]:            
                pe_ce_Diff = True
                pe = False
                arr_up = []
                for uppppp in up_price[0:2]:
                    up_ = (uppppp['PE']['changeinOpenInterest'] + uppppp['PE']['openInterest']) - (uppppp['CE']['changeinOpenInterest'] + uppppp['CE']['openInterest'])
                    arr_up.append(up_)
                sum_up = abs(arr_up[0] + arr_up[1])
                up_base_total = (down_price[-1]['PE']['changeinOpenInterest'] + down_price[-1]['PE']['openInterest']) - (down_price[-1]['CE']['changeinOpenInterest'] + down_price[-1]['CE']['openInterest'])
                if up_base_total > sum_up:
                    call_defs.append({"sum": up_base_total - sum_up, 'StockName': stock })
                    print(stock,up_base_total - sum_up)
                    stock_for_buy.objects.create(stocks_name=stock, call_or_put='CALL', difference_ce_pe=up_base_total - sum_up, PE_side_persnt = PE_side_persnt, CE_side_persnt = CE_side_persnt)            
            
            #### PUT
            elif up_price[0]['strikePrice'] == CEMaxValue[0]:
                pe_ce_Diff = True
                pe = True

                arr_down = []
                for downnnn in down_price[:-3:-1]:
                    down_ = (downnnn['PE']['changeinOpenInterest'] + downnnn['PE']['openInterest']) - (downnnn['CE']['changeinOpenInterest'] + downnnn['CE']['openInterest'])
                    arr_down.append(down_)
                sum_down = (arr_down[0] + arr_down[1])
                sum_down = abs(sum_down)
                down_base_total = (up_price[0]['PE']['changeinOpenInterest'] + up_price[0]['PE']['openInterest']) - (up_price[0]['CE']['changeinOpenInterest'] + up_price[0]['CE']['openInterest'])
                down_base_total = abs(down_base_total)
                if (down_base_total) > (sum_down):
                    if pcr <= 0.67:
                        put_defs.append({"sum": down_base_total - sum_down, 'StockName': stock})
                        # print(stock, down_base_total - sum_down)
                        stock_for_buy.objects.create(stocks_name=stock, call_or_put='PUT', difference_ce_pe=down_base_total - sum_down,PE_side_persnt = PE_side_persnt ,CE_side_persnt = CE_side_persnt)            

            else:
                pe_ce_Diff = False
                pe = False

            payload = {'name': stock, 'pcr': pcr, 'PE_CE_diffrent': pe_ce_Diff, 'CE': pe_ce_Diff, 'PE': pe}
            r = requests.put(
                "https://zerodha.harmistechnology.com/stockname", data=payload)
            success_count = success_count + 1
            # pcr_stock_name.objects.filter(name = stock).update(pcr =  pcr)
            print(stock, '->',pcr, '->', pe_ce_Diff)
            if stock == 'NO DATA':
                extra_setting.objects.filter(id = 1).update(pcr_isupdating = False)
        except Exception as e:
            print('Error-->',e)
            print('An exception occurred','->', stock)
            extra_setting.objects.filter(id = 1).update(pcr_isupdating = False)
            update_needed.append(stock)
            reject_count = reject_count + 1


    # sorted_call = sorted(call_defs, key=lambda i: -i['sum'])
    # sorted_put = sorted(put_defs, key=lambda j: -j['sum'])
    # if len(sorted_call) != 0:
    #     pass
    #     # stock_for_buy.objects.create(stocks_name=sorted_call[0]['StockName'], call_or_put='CALL')
    # if len(sorted_put) != 0: 
    #     pass   
    #     # stock_for_buy.objects.create(stocks_name=sorted_put[0]['StockName'], call_or_put='PUT')

    return render(request, "tailwind/PcrStock.html", { 'update_needed' : update_needed, 'success_count' : success_count, 'reject_count': reject_count })
# from rest_framework.pagination import PageNumberPagination

# class MyPaginationClass(PageNumberPagination):
#     page_size = 10  # Number of items to be included in each page
#     page_size_query_param = 'page_size'  # Parameter to specify the page size
#     max_page_size = 100  # Maximum page size allowed

#     def get_paginated_response(self, data):
#         return Response({
#             'next': self.get_next_link(),
#             'previous': self.get_previous_link(),
#             'count': self.page.paginator.count,
#             'results': data
#         })

#     def get_page_size(self, request):
#         page_size = request.query_params.get(self.page_size_query_param)
#         if page_size is not None:
#             try:
#                 page_size = int(page_size)
#                 if page_size > 0 and (not self.max_page_size or page_size <= self.max_page_size):
#                     return page_size
#             except (TypeError, ValueError):
#                 pass
#         return self.page_size

from .pagination import MyPaginationClass
class stock_details(APIView):
    # permission_classes = [IsAuthenticated]              
    # authentication_classes = [TokenAuthentication]
    # pagination_class = MyPaginationClass
    def get(self, request):
        queryset = stock_detail.objects.all().order_by("-buy_time")
        paginator = MyPaginationClass()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = stockListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
        
        
        # paginated_queryset = self.pagination_class.paginate_queryset(self, nse_objs, request, view=self)
        # # demo = stock_detail.objects.values_list().values()
        # serializer = stockListSerializer(paginated_queryset, many=True)
        # return self.pagination_class.get_paginated_response(serializer.data)


    def post(self, request):
        try:
            data = request.data
            # _mutable = data._mutable
            # data._mutable = True
            # print(data)
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
        obj = nse_setting.objects.get(id = pk)
        serializer = settingSerializer(obj, data = data, partial = True)

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
        try:
            snippet = self.get_object(pk)
            serializer = settingSerializer(snippet)
            return Response(serializer.data)        
        except:
            return Response({"message": "No Data Found"})     


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
    url = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
    headers = {'user-agent': 'my-app/0.0.1'}
    response = requests.get(url, headers=headers)
    data = response.json()
    timestamp = data['records']
    # print(data)
    return JsonResponse({"timestamp": timestamp })