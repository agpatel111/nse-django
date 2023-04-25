
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

from apscheduler.schedulers.background import BackgroundScheduler
from nse_app.Scheduler.BankNifty import BANKNIFTY
from nse_app.Scheduler.Nifty import NIFTY
from nse_app.Scheduler.Stock import StockCall, StockPut
from nse_app.Scheduler.PcrValues import PcrValues
from datetime import date


urlpatterns = [
    path("login", views.obtain_auth_token),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("", include("nse_app.urls")),
]


today = date.today()
start_date = str(today) + ' 09:15:00'
end_date = str(today) + ' 15:31:00'

scheduler = BackgroundScheduler()

# # scheduler.add_job(StockPut, "interval", minutes=0.5, start_date=start_date, end_date=end_date) 
# # scheduler.add_job(StockCall, "interval", minutes=0.5, start_date=start_date, end_date=end_date) 
scheduler.add_job(PcrValues, "interval", minutes=1, start_date=start_date, end_date=end_date)
scheduler.add_job(NIFTY, "interval", minutes=0.27, start_date=start_date, end_date=end_date) 
scheduler.add_job(BANKNIFTY, "interval", minutes=0.27, start_date=start_date, end_date=end_date)

scheduler.start()