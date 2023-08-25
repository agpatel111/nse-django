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
from nse_app.services import StockView, PcrUpdate
from nse_app.Scheduler.CoustomFun import Coustom
from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics
from .pagination import MyPaginationClass
from nse_app.Scheduler import SellFunction, BankNifty, NewBankNifty


def home(request):
    # BankNifty.BANKNIFTY()
    # NewBankNifty.BANKNIFTY()
    data = stock_detail.objects.all().order_by("-buy_time").values()
    paginator = Paginator(data, 25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    today = date.today()
        
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
    data = pcr_values.objects.filter().order_by("-timestamp")

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
    update_needed, success_count, reject_count = PcrUpdate.PcrUpdateFun()

    return render(request, "tailwind/PcrStock.html", { 'update_needed' : update_needed, 'success_count' : success_count, 'reject_count': reject_count })



class buyFutureOp(APIView):
    def post(self, request):
        try:
            if request.method == 'POST':
                option = request.data['OPTION']
                lots = request.data['lots']
                orderId = SellFunction.optionFuture(option, lots)
                print(orderId)
                return JsonResponse({'orderId': orderId})
            return JsonResponse('get method not allowed', safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class accountDetailsListCreateView(generics.ListCreateAPIView):
    queryset = AccountCredential.objects.all()
    serializer_class = accountDetailsSerializer
    
class accountDetailsRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AccountCredential.objects.all()
    serializer_class = accountDetailsSerializer

class stock_details(APIView):
    # permission_classes = [IsAuthenticated]              
    # authentication_classes = [TokenAuthentication]
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



class liveStocks(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        queryset = stock_detail.objects.filter(status = 'BUY', final_status='NA').order_by("-buy_time")
        paginator = MyPaginationClass()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = stockListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

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