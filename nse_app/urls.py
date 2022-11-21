from django.urls import path
from . import views


urlpatterns = [
    path('home/', views.home, name = 'home'),
    path('nse_data/', views.nse_data.as_view(), name = 'nse_data'),
    path('profits/', views.profits, name = 'profits'),

    path('profit/', views.profit.as_view(), name = 'profit'),
    path('datas/', views.datas, name = 'datas'),
    path('data/', views.data.as_view(), name = 'data'),
    path('nses/', views.nses, name = 'nses'),
    path('nse/', views.nsess.as_view(), name = 'nse'),
]
