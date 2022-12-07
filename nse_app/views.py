from django.shortcuts import render
from rest_framework.decorators import api_view , permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
# from knox.models import AuthToken
from .models import *
# from .forms import nse_dataForm
from .serializers import *
import datetime
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated 
from rest_framework.authentication import TokenAuthentication
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth.views import login

# Create your views here.

def home(request):
    data = stock_detail.objects.all().order_by("buy_time").values()
    return render(request, "nse.html", {"data": data})

class stock_details(APIView):
    # permission_classes = [IsAuthenticated]              
    # authentication_classes = [TokenAuthentication]

    def get(self, request):
        nse_objs = stock_detail.objects.all()
        serializer = stockListSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "stock details fetched", "data": serializer.data}
        )

    def post(self, request):

        try:
            data = request.data
            # _mutable = data._mutable
            # data._mutable = True
            serializer = stockPostSerializer(data=data)
            data["status"] = "BUY"
            # print(data["status"])
            # data["sell_buy_time"] = "-"
            # data._mutable = _mutable
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"status": True, "msg": "success post data", "data": serializer.data}
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
            data["status"] = "SELL"
            data["sell_buy_time"] = datetime.datetime.today()
            # print(data["sell_buy_time"] )
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "msg": "successfully SELL Stock",
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
    permission_classes = [IsAuthenticated]              
    authentication_classes = [TokenAuthentication]
    
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
    """
    Retrieve, update or delete a snippet instance.
    """
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


