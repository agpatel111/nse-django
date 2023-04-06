"""nse_data URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views

from apscheduler.schedulers.background import BackgroundScheduler
from nse_app.Scheduler.BankNifty import BANKNIFTY
from nse_app.Scheduler.Nifty import NIFTY
from nse_app.Scheduler.Stock import StockCall, StockPut, StockPcrCall, StockPcrPut



urlpatterns = [
    path("login", views.obtain_auth_token),
    path("api-auth/", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("", include("nse_app.urls")),
]



scheduler = BackgroundScheduler()

# scheduler.add_job(PcrValues, "interval", minutes=5, id='PcrValues_001')
# scheduler.add_job(StockPcrPut, "interval", minutes=0.27, id='Stock_001')
# scheduler.add_job(NIFTY, "interval", minutes=0.27, id='nifty_001',) 
# scheduler.add_job(BANKNIFTY, "interval", minutes=0.27, id='banknifty_001')

scheduler.start()