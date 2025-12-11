from django.urls import path
from . import views

# Define the application namespace
app_name = 'shop'

urlpatterns = [
    
    # 1. TRANSACTION VIEWS (MUST COME FIRST TO AVOID CLASHES)
    
    # 1.1. Maps the required name 'buy_paper' to the view that needs the paper_slug
    path('buy/<slug:paper_slug>/', views.initiate_payment, name='buy_paper'),
    
    # 1.2. /payment/callback/ - Handles user redirection from Paystack
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    
    # 1.3. /webhooks/paystack/ - Receives background confirmation from Paystack
    path('webhooks/paystack/', views.paystack_webhook, name='paystack_webhook'),
    
    # 2. PLACEHOLDER VIEWS (Hardcoded names that must also come before slugs)
    path('profile/', views.profile, name='profile'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # 3. NAVIGATION VIEWS (Generic slug patterns MUST COME LAST)
    
    # 3.1. / (Homepage) - Lists all Classes/Grades
    path('', views.class_list, name='class_list'),
    
    # 3.2. /<class_slug>/ - Lists all Terms for a Class
    path('<slug:class_slug>/', views.term_list, name='term_list'),
    
    # 3.3. /<class_slug>/<term_slug>/ - Lists all Subjects for a Term
    path('<slug:class_slug>/<slug:term_slug>/', views.subject_list, name='subject_list'),
    
    # 3.4. /<class_slug>/<term_slug>/<subject_slug>/<paper_slug>/ - Paper Detail/Product Page
    path('<slug:class_slug>/<slug:term_slug>/<slug:subject_slug>/<slug:paper_slug>/', 
         views.paper_detail, 
         name='paper_detail'),
]