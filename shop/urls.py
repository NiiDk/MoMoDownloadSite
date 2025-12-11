# shop/urls.py (Replace the entire file content with this)

from django.urls import path
from . import views

# Define the application namespace
app_name = 'shop'

urlpatterns = [
    
    # 1. TRANSACTION / DOWNLOAD VIEWS
    
    path('buy/<slug:paper_slug>/', views.initiate_payment_or_download, name='buy_paper'),
    path('free-download/<slug:paper_slug>/', views.free_download_landing, name='download_page'),
    path('download-file/<slug:paper_slug>/', views.download_file, name='download_file'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('webhooks/paystack/', views.paystack_webhook, name='paystack_webhook'),
    
    # 2. PLACEHOLDER VIEWS
    path('profile/', views.profile, name='profile'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # --- NEW CONTACT ENDPOINTS ---
    # Renders the contact form page (GET)
    path('contact/', views.contact, name='contact'), 
    # API endpoint for AJAX submission (POST)
    path('api/contact/', views.contact_view, name='contact_api'),
    # --- END NEW CONTACT ENDPOINTS ---

    # 3. NAVIGATION VIEWS (Generic slug patterns MUST COME LAST)
    
    path('', views.class_list, name='class_list'),
    path('<slug:class_slug>/', views.term_list, name='term_list'),
    path('<slug:class_slug>/<slug:term_slug>/', views.subject_list, name='subject_list'),
    path('<slug:class_slug>/<slug:term_slug>/<slug:subject_slug>/<slug:paper_slug>/', 
         views.paper_detail, 
         name='paper_detail'),
]