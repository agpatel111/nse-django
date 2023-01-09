from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(nse_setting)

admin.site.register(stock_detail)

admin.site.register(pcr_stock_name)

admin.site.register(Category)

admin.site.register(live)