# MoMoDownloadSite/urls.py

from django.contrib import admin
from django.urls import path, include # 'include' is necessary for this structure
from shop import views 

urlpatterns = [
    # Admin path remains the same
    path('admin/', admin.site.urls),

    # 🔥 Point the root path to the shop app's URLs
    path('', include('shop.urls')),

    # The webhook MUST remain here for the Paystack link to be at the root level (e.g., /webhooks/paystack/)
    path('webhooks/paystack/', views.paystack_webhook, name='paystack-webhook'),
]