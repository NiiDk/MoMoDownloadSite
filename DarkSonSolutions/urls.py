# MoMoDownloadSite/MoMoDownloadSite/urls.py

from django.contrib import admin
from django.urls import path, include
# CRITICAL: This imports the webhook from the correct 'shop' views file.
from shop.views import paystack_webhook 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # All base URLs ('') are now routed to the 'shop' app.
    path('', include('shop.urls')), 
    
    # Paystack webhook URL must be at the root.
    path('webhooks/paystack/', paystack_webhook, name='paystack-webhook'),
]