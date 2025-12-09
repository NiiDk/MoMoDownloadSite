# MoMoDownloadSite/shop/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # The actual homepage for the 'shop' app
    path('', views.paper_list, name='paper-list'), 

    # Payment Initiation
    path('buy/<int:paper_id>/', views.initiate_payment, name='initiate-payment'),

    # Payment Callback
    path('payment/callback/', views.payment_callback, name='payment-callback'),
]