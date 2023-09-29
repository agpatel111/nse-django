from .models import *
from .serializers import *
from django.shortcuts import render, redirect
from django.http import JsonResponse
from datetime import date
from nse_app.services import PcrUpdate
from django.core.paginator import Paginator
from django.utils import timezone
from openpyxl import Workbook
from django.http import HttpResponse
import pytz

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
    return render(request, "Home.html", {"data": page.object_list, 'pagination_info': pagination_info, 'today': today})


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

    return render(request, 'PcrValues.html', {'data': data})

def settings(request):
    data = live.objects.all()
    return render(request, 'settings.html', { 'data' : data })


def export_to_excel(request):
    kolkata_timezone = pytz.timezone('Asia/Kolkata')
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="orders.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Order Data"

    headers = ["id", "option","Type", "Strike Price", "Live Price", "Buy Price", "Buy time", "TP", "SL", "Buy PCR", "Exit PCR", "Exit Price", "Exit time", "P&L", "Oi Deff", "qty"]
    ws.append(headers)

    kolkata_timezone = pytz.timezone('Asia/Kolkata')
    products = stock_detail.objects.all().order_by('-buy_time')
    for i in products:
        print("i.sell_buy_time", i.sell_buy_time)
        ws.append([
            i.id,
            i.percentage.option, 
            i.type, 
            i.base_strike_price, 
            i.live_Strike_price, 
            i.buy_price, 
            (i.buy_time).astimezone(kolkata_timezone).replace(tzinfo=None),
            i.sell_price, 
            i.stop_loseprice, 
            i.buy_pcr, 
            i.exit_pcr, 
            i.exit_price, 
            ((i.sell_buy_time).astimezone(kolkata_timezone).replace(tzinfo=None)) if i.sell_buy_time else i.sell_buy_time,
            i.final_status, 
            i.oi_diff,
            i.qty, 
            ])

    wb.save(response)
    return response


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

def pcrUpdate(request):
    update_needed, success_count, reject_count = PcrUpdate.PcrUpdateFun()

    return render(request, "PcrStock.html", { 'update_needed' : update_needed, 'success_count' : success_count, 'reject_count': reject_count })



