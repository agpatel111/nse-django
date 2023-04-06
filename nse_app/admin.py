from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(nse_setting)
class nsesetting(admin.ModelAdmin):
    list_display = ['option', 'profit_percentage', 'loss_percentage', 'set_pcr', 'baseprice_plus' ]

@admin.register(stock_detail)
class nsestock(admin.ModelAdmin):
    list_display = ['percentage', 'base_strike_price', 'buy_price', 'exit_price', 'buy_time', 'final_status', 'stock_name']

@admin.register(pcr_stock_name)
class pcrstock(admin.ModelAdmin):
    list_display = ['name', 'pcr', 'date']

@admin.register(live)
class live(admin.ModelAdmin):
    list_display = ['live_banknifty', 'live_nifty', 'live_stock_ce', 'live_stock_pe']

@admin.register(pcr_option)
class live(admin.ModelAdmin):
    list_display = ['OptionName', 'AtSetPcr', 'PcrStopLoss', 'LivePcr']