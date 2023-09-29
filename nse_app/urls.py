from django.urls import path
from . import views
from . import views_api

app_name = "nse_app"

urlpatterns = [
    path('', views.home, name = 'home'),
    path('home/', views.home, name = 'home'),
    path('deleteOrder/', views.deleteStock, name = 'deletestock'),

    path('settings/', views.settings, name = 'settings'),
    path('changesettings/', views.changesettings, name = 'changesettings'),

    path('pcrvalues/', views.PcrValue, name = 'pcrvalues'),
    path('pcrUpdate/', views.pcrUpdate, name = 'pcrUpdate'),

    path('export/', views.export_to_excel, name='export_to_excel'),


    # API
    path('logout', views_api.Logout.as_view(), name="logout"),
    
    path('buyFutureOp', views_api.buyFutureOp.as_view(), name = 'buyFutureOp'),
    path('buyStockFuture', views_api.buyStockFuture.as_view(), name = 'buyStockFuture'),

    ## SETTING API
    path('setting_nse', views_api.setting_nse.as_view(), name = 'setting_nse'), 
    path("get_setting_data/<int:pk>", views_api.SnippetDetail.as_view(), name="setting_nse"),
    path('patch_stock/<int:pk>', views_api.patch_stock, name = 'patch-stock'),
    path('delete_stock/<int:pk>', views_api.delete_stock, name = 'delete-stock'),
    
    path('accountdetail/', views_api.accountDetailsListCreateView.as_view(), name='accountDetailsListCreateView'),
    path('accountdetail/<int:pk>', views_api.accountDetailsRetrieveUpdateDeleteView.as_view(), name='accountDetailsRetrieveUpdateDeleteView'),
    
    path('stocks', views_api.stock_details.as_view(), name = 'stock_detail'),
    path('liveStocks', views_api.liveStocks.as_view(), name = 'liveStocks'), 
    path('stockname', views_api.PcrStockName.as_view(), name = 'stockname'),
    
    ## GET NSEDATA
    path('api/stockData', views_api.stockData, name = 'apistock'),
    path('api/getStock/<slug:stockname>', views_api.getStock, name = 'getStock'),
    

]
