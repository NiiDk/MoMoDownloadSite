# shop/urls.py

from django.urls import path
from . import views

# Define the application namespace
app_name = 'shop'

urlpatterns = [
    # ====================================================================
    # 0. STATIC PAGES & UTILITY VIEWS (No slugs)
    # ====================================================================
    
    # 0.1. Homepage - Lists all Classes/Grades (should come first)
    path('', views.class_list, name='class_list'),
    
    # 0.2. User Account Pages (static paths)
    path('profile/', views.profile, name='profile'),
    path('history/', views.purchase_history, name='purchase_history'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    
    # 0.3. Contact Us Page
    path('contact/', views.contact_us, name='contact_us'),
    
    # 0.4. Static information pages (if needed)
    path('about/', views.about, name='about'),
    path('faq/', views.faq, name='faq'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    
    # ====================================================================
    # 1. TRANSACTION & DOWNLOAD VIEWS (Specific paper slugs)
    # ====================================================================
    
    # 1.1. Payment initiation for specific paper
    path('buy/<slug:paper_slug>/', views.initiate_payment_or_download, name='buy_paper'),
    
    # 1.2. Free download landing page
    path('free-download/<slug:paper_slug>/', views.free_download_landing, name='download_page'),
    
    # 1.3. Actual file download endpoint
    path('download-file/<slug:paper_slug>/', views.download_file, name='download_file'),
    
    # 1.4. Download all papers for a subject as ZIP (new feature)
    path('download-subject/<slug:class_slug>/<slug:term_slug>/<slug:subject_slug>/',
         views.download_subject_zip, 
         name='download_subject_zip'),
    
    # 1.5. Payment callback from Paystack
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    
    # 1.6. Paystack webhook endpoint
    path('webhooks/paystack/', views.paystack_webhook, name='paystack_webhook'),
    
    # 1.7. Payment status check
    path('payment/status/<str:reference>/', views.payment_status, name='payment_status'),
    
    # ====================================================================
    # 2. NAVIGATION & BROWSE VIEWS (Hierarchical slugs)
    # ====================================================================
    
    # 2.1. Class level - List all terms for a class
    # This must come AFTER 'buy/' to avoid conflict
    path('class/<slug:class_slug>/', views.term_list, name='term_list'),
    
    # 2.2. Term level - List all subjects for a term
    path('class/<slug:class_slug>/term/<slug:term_slug>/', 
         views.subject_list, 
         name='subject_list'),
    
    # 2.3. Subject level - List ALL papers for a subject (NEW)
    # IMPORTANT: This must come BEFORE the paper detail pattern
    path('class/<slug:class_slug>/term/<slug:term_slug>/subject/<slug:subject_slug>/',
         views.subject_papers_list,
         name='subject_papers_list'),
    
    # 2.4. Paper detail view
    path('class/<slug:class_slug>/term/<slug:term_slug>/subject/<slug:subject_slug>/paper/<slug:paper_slug>/',
         views.paper_detail,
         name='paper_detail'),
    
    # ====================================================================
    # 3. SEARCH & FILTER VIEWS (Optional enhancements)
    # ====================================================================
    
    # 3.1. Search papers
    path('search/', views.search_papers, name='search_papers'),
    
    # 3.2. Browse all papers (without hierarchy)
    path('papers/', views.all_papers, name='all_papers'),
    
    # 3.3. Browse by year
    path('papers/year/<int:year>/', views.papers_by_year, name='papers_by_year'),
    
    # 3.4. Browse by exam type
    path('papers/type/<str:exam_type>/', views.papers_by_type, name='papers_by_type'),
    
    # ====================================================================
    # 4. API ENDPOINTS (For AJAX functionality)
    # ====================================================================
    
    # 4.1. Check if paper is free (AJAX)
    path('api/paper/<slug:paper_slug>/status/', views.api_paper_status, name='api_paper_status'),
    
    # 4.2. Get paper preview info (AJAX)
    path('api/paper/<slug:paper_slug>/preview/', views.api_paper_preview, name='api_paper_preview'),
    
    # 4.3. Track paper views (AJAX)
    path('api/paper/<slug:paper_slug>/track-view/', views.api_track_view, name='api_track_view'),
    
    # 4.4. Contact form submission (AJAX)
    path('api/contact/submit/', views.api_contact_submit, name='api_contact_submit'),
]