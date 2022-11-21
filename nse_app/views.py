from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .forms import nse_dataForm
from .serializers import *

# Create your views here.


def home(request):
    form = nse_dataForm()
    data = nse_model.objects.all()
    return render(request, "base.html", {"form": form, "data": data})


class nse_data(APIView):
    def get(self, request):
        nse_objs = nse_model.objects.all()
        serializer = nse_dataSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "nse-data fetched", "data": serializer.data}
        )

    def post(self, request):
        try:
            data = request.data
            serializer = nse_dataSerializer(data=data)
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


def profits(request):

    data = nse_profit.objects.all()
    return render(request, "base.html", {"data": data})


class profit(APIView):
    def get(self, request):
        nse_objs = nse_profit.objects.all()
        serializer = nse_profitSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "nse_profit fetched", "data": serializer.data}
        )

    def post(self, request):
        try:
            data = request.data
            serializer = nse_profitSerializer(data=data)
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


def datas(request):

    data = nse_profit.objects.all()
    return render(request, "datas.html", {"data": data})


class data(APIView):
    def get(self, request):
        print("hello")
        nse_objs = nse_data.objects.all()
        serializer = nse_s_Serializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "nse_profit fetched", "data": serializer.data}
        )

    def post(self, request):
        try:
            data = request.data
            serializer = nse_s_Serializer(data=data)
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


def nses(request):

    data = nse.objects.all().order_by("buy_time").values()
    return render(request, "nse.html", {"data": data})


class nsess(APIView):
    # print("gehehe")
    def get(self, request):
        # print("hello")
        nse_objs = nse.objects.all()
        serializer = nseSerializer(nse_objs, many=True)
        return Response(
            {"status": True, "msg": "nse_profit fetched", "data": serializer.data}
        )

    def post(self, request):
        print("in post")
        try:
            data = request.data
            # _mutable = data._mutable
            # data._mutable = True
            serializer = nseSerializer(data=data)
            data["buy_status"] = "BUY"
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


    def patch(self,request):
        try:
            data = request.data
            if not data.get("uid"):
                return Response({"status": False, "msg": "uid is required", "data": {}})

            obj = nse.objects.get(uid=data.get("uid"))
            serializer = nseSerializer(obj, data=data, partial=True)
            data["buy_status"] = "SELL"
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
            return Response({"status": False, "msg": "Invalid uid", "data": {}})
