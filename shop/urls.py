# shop/urls.py

from django.urls import path
from . import views

app_name = 'shop' # CRITICAL: Namespace for URL reversing

urlpatterns = [
    # --- 1. Top Level: Homepage (Display all Classes/Grades) ---
    # The new homepage will show a list of all available Classes (e.g., JHS 1, Basic 7)
    path('', views.class_list, name='class_list'), 
    
    # --- 2. Second Level: Term Selection ---
    # Path: /class/jhs-1/ (Shows Term 1, Term 2, Term 3 for JHS 1)
    path('class/<slug:class_slug>/', views.term_list, name='term_list'),
    
    # --- 3. Third Level: Subject Selection ---
    # Path: /class/jhs-1/term/term-1/ (Shows 10 Subjects for JHS 1 Term 1)
    path('class/<slug:class_slug>/term/<slug:term_slug>/', 
         views.subject_list, 
         name='subject_list'),

    # --- 4. Final Level: Paper Detail/Buy Page ---
    # Path: /class/jhs-1/term/term-1/subject/mathematics/paper-slug/
    # Note: We use the subject_slug, but this view lists the paper directly.
    path('class/<slug:class_slug>/term/<slug:term_slug>/subject/<slug:subject_slug>/paper/<slug:paper_slug>/',
         views.paper_detail,
         name='paper_detail'),


    # --- 5. Payment Flow (Kept and Updated) ---
    
    # Payment Initiation - Now uses paper_slug instead of ID for cleaner URLs
    path('buy/<slug:paper_slug>/', views.initiate_payment, name='initiate_payment'),

    # Payment Callback
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    
    # Webhook Endpoint (Assume you have this in your main project urls.py, 
    # but we will add it here for completeness if it wasn't external)
    # path('webhooks/paystack/', views.paystack_webhook, name='paystack_webhook'),
]