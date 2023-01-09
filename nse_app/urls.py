from django.urls import path
from . import views
from nse_app.Scheduler import Nifty
# from knox import views as knox_views

app_name = "nse_app"

urlpatterns = [
    path('home/', views.home, name = 'home'),
    path('test/', views.print_hello, name = 'test'),
    path('pcr/', views.pcr, name = 'pcr'),
    
    path('stocks', views.stock_details.as_view(), name = 'stock_detail'),
    
    path('setting_nse', views.setting_nse.as_view(), name = 'setting_nse'), 

    path('stockname', views.PcrStockName.as_view(), name = 'stockname'), 

  
    path("get_setting_data/<int:pk>", views.SnippetDetail.as_view(), name="setting_nse"),
    path('delete_stock/<int:pk>', views.delete_stock, name = 'delete-stock'),
    path('patch_stock/<int:pk>', views.patch_stock, name = 'patch-stock'),
    path('Logout', views.Logout.as_view(), name="logout"),
  
]
