
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

from apscheduler.schedulers.background import BackgroundScheduler
from nse_app.Scheduler.BankNifty import BANKNIFTY
from nse_app.Scheduler.Nifty import NIFTY
from nse_app.Scheduler.PcrValues import PcrValues
from nse_app.Scheduler.Stock import stockFutureSell


urlpatterns = [
    path("login", views.obtain_auth_token),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("", include("nse_app.urls")),
    path("__debug__/", include("debug_toolbar.urls")),

]

''' Call Function at every set time using apscheduler '''

scheduler = BackgroundScheduler()
scheduler.add_job(stockFutureSell, "interval", minutes=0.27, id='StockFuture')
scheduler.add_job(PcrValues, "interval", minutes=1, id='PcrValues_001')
scheduler.add_job(NIFTY, "interval", minutes=0.27, id='nifty_001',) 
scheduler.add_job(BANKNIFTY, "interval", minutes=0.27, id='banknifty_001')
scheduler.start()
