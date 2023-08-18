from django.urls import path
from . import views
from nse_app.Scheduler import Nifty

app_name = "nse_app"

urlpatterns = [
    path('', views.home, name = 'home'),
    path('home/', views.home, name = 'home'),
    path('deletestock/<int:id>', views.deleteStock, name = 'deletestock'),

    path('settings/', views.settings, name = 'settings'),
    path('changesettings/', views.changesettings, name = 'changesettings'),

    path('pcrvalues/', views.PcrValue, name = 'pcrvalues'),
    path('pcr/', views.pcrUpdate, name = 'pcrUpdate'),
    
    path('stocks', views.stock_details.as_view(), name = 'stock_detail'),
    path('stockname', views.PcrStockName.as_view(), name = 'stockname'),
     
    ## SETTING API
    path('accountdetail/', views.accountDetailsListCreateView.as_view(), name='accountDetailsListCreateView'),
    path('accountdetail/<int:pk>', views.accountDetailsRetrieveUpdateDeleteView.as_view(), name='accountDetailsRetrieveUpdateDeleteView'),
    
    path('setting_nse', views.setting_nse.as_view(), name = 'setting_nse'), 
    path("get_setting_data/<int:pk>", views.SnippetDetail.as_view(), name="setting_nse"),
    path('patch_stock/<int:pk>', views.patch_stock, name = 'patch-stock'),
    path('delete_stock/<int:pk>', views.delete_stock, name = 'delete-stock'),
    
    ## GET NSEDATA
    path('api/stockData', views.stockData, name = 'apistock'),
    path('getStock/<slug:slug>', views.getStock, name = 'getStock'),

    
    path('logout', views.Logout.as_view(), name="logout"),


    path('print_hello/', views.print_hello, name = 'print_hello'),
  
  
]
