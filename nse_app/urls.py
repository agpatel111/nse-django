from django.urls import path
from . import views
from nse_app.Scheduler import Nifty

app_name = "nse_app"

urlpatterns = [
    path('', views.home, name = 'home'),
    path('home/', views.home, name = 'home'),
    path('deletestock/<int:id>', views.deleteStock, name = 'deletestock'),
    path('pcrvalues/', views.PcrValue, name = 'pcrvalues'),
    path('settings/', views.settings, name = 'settings'),
    path('changesettings/', views.changesettings, name = 'changesettings'),
    path('pcr/', views.pcrUpdate, name = 'pcrUpdate'),
    path('getStock/<slug:slug>', views.getStock, name = 'getStock'),
    path('api/stockData', views.stockData, name = 'apistock'),
    path('print_hello/', views.print_hello, name = 'print_hello'),
    
    path('stocks', views.stock_details.as_view(), name = 'stock_detail'),
    
    path('setting_nse', views.setting_nse.as_view(), name = 'setting_nse'), 

    path('stockname', views.PcrStockName.as_view(), name = 'stockname'), 

  
    path("get_setting_data/<int:pk>", views.SnippetDetail.as_view(), name="setting_nse"),
    path('delete_stock/<int:pk>', views.delete_stock, name = 'delete-stock'),
    path('patch_stock/<int:pk>', views.patch_stock, name = 'patch-stock'),
    path('Logout', views.Logout.as_view(), name="logout"),
  
]
