from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(nse_model)

admin.site.register(nse_profit)
admin.site.register(nse_data)
admin.site.register(nse)