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
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import date, datetime, timedelta
from nse_app.services import StockView, PcrUpdate
from django.core.paginator import Paginator
from django.utils import timezone
from rest_framework import generics
from .pagination import MyPaginationClass
from nse_app.Scheduler import SellFunction, BankNifty, NewBankNifty

def home(request):
    data = stock_detail.objects.select_related('percentage').all().order_by("-buy_time")
    paginator = Paginator(data, 25)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    today = timezone.now().date()
    today = timezone.make_aware(timezone.datetime(today.year, today.month, today.day))

    # profit_records = stock_detail.objects.select_related('percentage').filter(
    #     buy_time__gte=today
    # )
    # total_profit = 0.0  
    # for record in profit_records:
    #     if record.final_status != 'NA':
    #         option = record.percentage.option.split()[0]
    #         if option == 'BANKNIFTY' and record.exit_price:
    #             total_profit += (record.exit_price - record.buy_price) * 15
    #         elif option == 'NIFTY' and record.exit_price:
    #             total_profit += (record.exit_price - record.buy_price) * 50

    for i in page.object_list:
        option = i.percentage.option.split()
        if option[0] == 'BANKNIFTY' and i.exit_price:
            if option[1] == 'FUTURE' and i.type == 'SELL':
                i.PL = '%.2f'% ((i.buy_price - i.exit_price) * 15)
            else:
                i.PL = '%.2f'% ((i.exit_price - i.buy_price) * 15)
        elif option[0] == 'NIFTY' and i.exit_price:
            if option[1] == 'FUTURE' and i.type == 'SELL':
                i.PL = '%.2f'% ((i.buy_price - i.exit_price) * 50)
            else:
                i.PL = '%.2f'% ((i.exit_price - i.buy_price) * 50)
        elif option[0] == 'STOCK' and i.exit_price:
            if option[1] == 'FUTURE' and i.type == 'SELL':
                i.PL = '%.2f'% ((i.buy_price - i.exit_price) * i.qty)
            else:
                i.PL = '%.2f'% ((i.exit_price - i.buy_price) * i.qty)
        else:
            i.PL = '-'

    
    pagination_info = {
    'page': page,
    'paginator': paginator,
    }
    return render(request, "tailwind/Home.html", {"data": page.object_list, 'pagination_info': pagination_info, 'today': today})


def deleteStock(request):
    if request.method == "POST":
        id = request.POST.get('id')
        stock =  stock_detail.objects.get(id = id)
        stock.delete()
        return JsonResponse({'status' : 1})
    else:
        return JsonResponse({'status' : 0})

def PcrValue(request):
    today = date.today()
    today = timezone.make_aware(timezone.datetime(today.year, today.month, today.day))
    data = pcr_values.objects.filter(timestamp__gte = today).order_by("-timestamp")

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
def getStock(request, stockname):
    name = stockname
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
            option = request.data['OPTION']
            type = request.data['type']
            lots = request.data['lots']
            profit = request.data['profit']
            loss = request.data['loss']
            if option == 'BANKNIFTY': optionId = nse_setting.objects.filter(option = "BANKNIFTY FUTURE").values().first()
            if option == 'NIFTY': optionId = nse_setting.objects.filter(option = "NIFTY FUTURE").values().first()
            obj = SellFunction.optionFuture(option, lots, profit, loss, type)

            stock_detail.objects.create(status="BUY", type= type , buy_price=obj['ltp'], sell_price = obj['squareoff'], stop_loseprice = obj['stoploss'], order_id = obj['orderId'], percentage_id=optionId['id'])
            
            return JsonResponse({'orderId': obj['orderId']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class buyStockFuture(APIView):
    def post(self, request):
        try:
            stock = request.data['STOCK']
            type = request.data['type']
            lots = request.data['lots']
            profit = request.data['profit']
            loss = request.data['loss']
            obj = nse_setting.objects.filter(option = "STOCK FUTURE").values().first()

            ltp, squareoff, stoploss, orderId, qty = SellFunction.stockFutureBuyPrice(stock, lots, profit, loss, type)
            stock_detail.objects.create(status="BUY", type= type, stock_name = stock, qty = qty,  buy_price=ltp, sell_price = squareoff, stop_loseprice = stoploss, order_id = orderId, percentage_id=obj['id'])
            
            return JsonResponse({'orderId': ltp})
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
        
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        try:
            if start_date and end_date:
                start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)) - timedelta(seconds=1)

                queryset = stock_detail.objects.select_related('percentage').filter(buy_time__gte = start_date, buy_time__lte=end_date).order_by("-buy_time")
                total_PL = sum(stockListSerializer().get_PL(record) or 0 for record in queryset)
            else:
                queryset = stock_detail.objects.select_related('percentage').all().order_by("-buy_time")
                total_PL = 0
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # queryset = stock_detail.objects.select_related('percentage').all().order_by("-buy_time")
        paginator = MyPaginationClass()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = stockListSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response({'total_PL': total_PL,'data': serializer.data})


    def put(self, request):
        try:
            data = request.data
            if not data.get("id"):
                return Response({"status": False, "message": "id is required", "data": {}})

            obj = stock_detail.objects.get(id=data.get("id"))
            serializer = stockPostSerializer(obj, data=data, partial=True)
            if ('exit_price' in data):
                data["status"] = "SELL"
                data["sell_buy_time"] = datetime.today()
            if serializer.is_valid():
                serializer.save()
                return Response({
                        "status": True,
                        "message": "Successfully SELL Stock",
                        "data": serializer.data,
                    })
            else:
                return Response({
                        "status": False,
                        "message": "invalid data",
                        "data": serializer.errors,
                    })
        except Exception as e:
            return Response({"status": False, "message": "Invalid id", "data": {}})    


class liveStocks(APIView):
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        queryset = stock_detail.objects.filter(status = 'BUY').order_by("-buy_time")
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
