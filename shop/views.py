# shop/views.py

import json
import requests
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, FileResponse, Http404 
from django.urls import reverse
from django.db import models
from django.core.mail import send_mail # <--- NEW IMPORT
from .models import Classes, Term, Subject, QuestionPaper, Payment
import os 

# ====================================================================
# 1. HIERARCHICAL LIST VIEWS (Navigation)
# ====================================================================

# ... existing imports ...

# ====================================================================
# 1. HIERARCHICAL LIST VIEWS (Navigation)
# ====================================================================

# 1.1. Homepage: List all Classes/Grades
def class_list(request):
    classes = Classes.objects.annotate(
        paper_count=models.Count('papers', filter=models.Q(papers__is_available=True))
    ).order_by('order', 'name')
    
    context = {
        'classes': classes,
        'page_title': 'Select Your Class/Grade',
        'is_homepage': True
    }
    return render(request, 'shop/class_list.html', context)
    
# 1.2. Second Level: List all Terms for a Class
def term_list(request, class_slug):
    class_level = get_object_or_404(Classes, slug=class_slug)
    
    terms = Term.objects.filter(class_name=class_level).annotate(
        paper_count=models.Count('papers', filter=models.Q(papers__is_available=True))
    ).order_by('order', 'name')
    
    context = {
        'class_level': class_level,
        'terms': terms,
        'page_title': f'Select Term for {class_level.name}',
    }
    return render(request, 'shop/term_list.html', context)

# 1.3. Third Level: List all Subjects for a Term (UPDATED)
def subject_list(request, class_slug, term_slug):
    """
    Displays ALL subjects and ALL papers for each subject.
    """
    class_level = get_object_or_404(Classes, slug=class_slug)
    term = get_object_or_404(Term, class_name=class_level, slug=term_slug)
    
    # Get ALL available papers for this class and term
    all_papers = QuestionPaper.objects.filter(
        class_level=class_level,
        term=term,
        is_available=True
    ).select_related('subject').order_by('subject__name', '-year', 'exam_type')
    
    # Group papers by subject
    papers_by_subject = {}
    for paper in all_papers:
        if paper.subject_id not in papers_by_subject:
            papers_by_subject[paper.subject_id] = {
                'subject': paper.subject,
                'papers': []
            }
        papers_by_subject[paper.subject_id]['papers'].append(paper)
    
    # Get all subjects (including those without papers)
    all_subjects = Subject.objects.all().order_by('name')
    
    # Prepare final subjects list
    subjects_list = []
    for subject in all_subjects:
        if subject.id in papers_by_subject:
            subjects_list.append(papers_by_subject[subject.id])
        else:
            subjects_list.append({
                'subject': subject,
                'papers': []
            })
    
    context = {
        'class_level': class_level,
        'term': term,
        'subjects_list': subjects_list,
        'total_papers': all_papers.count(),
        'page_title': f'{class_level.name} {term.name} - Select Subject',
    }
    return render(request, 'shop/subject_list.html', context)

# 1.4. NEW: Subject Papers List View
def subject_papers_list(request, class_slug, term_slug, subject_slug):
    """
    Shows ALL papers for a specific subject in a class and term.
    """
    class_level = get_object_or_404(Classes, slug=class_slug)
    term = get_object_or_404(Term, class_name=class_level, slug=term_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)
    
    papers = QuestionPaper.objects.filter(
        class_level=class_level,
        term=term,
        subject=subject,
        is_available=True
    ).order_by('-year', 'exam_type', 'title')
    
    context = {
        'class_level': class_level,
        'term': term,
        'subject': subject,
        'papers': papers,
        'paper_count': papers.count(),
        'page_title': f'{class_level.name} {term.name} - {subject.name} Papers',
    }
    return render(request, 'shop/subject_papers_list.html', context)

# 1.5. Final Level: Paper Detail/Buy Page
def paper_detail(request, class_slug, term_slug, subject_slug, paper_slug):
    paper = get_object_or_404(QuestionPaper, 
        class_level__slug=class_slug,
        term__slug=term_slug,
        subject__slug=subject_slug,
        slug=paper_slug,
        is_available=True
    )
    
    # Increment view count
    paper.increment_views()
    
    # Get related papers (other papers in same subject)
    related_papers = QuestionPaper.objects.filter(
        class_level=paper.class_level,
        term=paper.term,
        subject=paper.subject,
        is_available=True
    ).exclude(id=paper.id).order_by('-year')[:5]
    
    if paper.is_paid:
        button_url = reverse('shop:buy_paper', args=[paper.slug])
        button_text = "Buy Now & Get Password via SMS"
    else:
        button_url = reverse('shop:download_page', args=[paper.slug])
        button_text = "Free Download"
    
    context = {
        'paper': paper,
        'related_papers': related_papers,
        'page_title': paper.get_display_title(),
        'currency_code': settings.CURRENCY_CODE,
        'button_url': button_url,
        'button_text': button_text
    }
    return render(request, 'shop/paper_detail.html', context)

# ... rest of the views remain the same ...


# ====================================================================
# 2. FORM DEFINITION (ADD CONTACT FORM)
# ====================================================================

class PurchaseForm(forms.Form):
    """Simple form for user input (email and phone number)"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label='Mobile Money Number (e.g., 024xxxxxxx)',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


class ContactForm(forms.Form):
    """Simple form for contact enquiries."""
    name = forms.CharField(
        label='Your Name',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., John Doe'})
    )
    email = forms.EmailField(
        label='Your Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@domain.com'})
    )
    subject = forms.CharField(
        label='Subject',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enquiry about pricing'})
    )
    message = forms.Field(
        label='Your Message / Suggestion',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please type your message here...'})
    )


# ====================================================================
# 3. MAIN CONDITIONAL LOGIC & PAYMENT INITIATION
# ====================================================================

def initiate_payment_or_download(request, paper_slug):
    """
    Handles 'shop:buy_paper'. Checks the 'is_paid' flag:
    - If False (free), redirects to the new free download landing page.
    - If True (paid), proceeds with Paystack payment initiation form.
    """
    try:
        paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    except Exception:
        return render(request, 'shop/error.html', {'message': 'The requested item was not found.'})

    # === CONDITIONAL LOGIC ===
    if not paper.is_paid:
        # If the paper is FREE, redirect to the new landing page
        return redirect('shop:download_page', paper_slug=paper.slug)
    
    # === ORIGINAL PAID LOGIC (IF is_paid is checked/True) ===
    if request.method == 'POST':
        form = PurchaseForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']

            # 1. Create the local Payment record (unverified)
            payment = Payment.objects.create(
                question_paper=paper,
                email=email,
                phone_number=phone_number
            )
            
            # 2. Paystack API Call Setup
            url = "https://api.paystack.co/transaction/initialize"
            headers = {
                "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "email": email,
                "amount": payment.amount_in_kobo(),
                "currency": settings.CURRENCY_CODE,
                "reference": str(payment.ref),
                "callback_url": f"{request.scheme}://{request.get_host()}{reverse('shop:payment_callback')}",
                "channels": ["mobile_money"],
            }
            
            # 3. Make the request to Paystack
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status'):
                return redirect(response_data['data']['authorization_url'])
            else:
                print(f"Paystack Error: {response_data}") 
                return render(request, 'shop/error.html', {'message': response_data.get('message', 'Could not initiate payment.')})
    
    # Initial GET request for PAID papers: Display the form
    else:
        form = PurchaseForm()

    return render(request, 'shop/buy_paper.html', {'form': form, 'paper': paper})


# ====================================================================
# 4. FREE DOWNLOAD LANDING PAGE
# ====================================================================

def free_download_landing(request, paper_slug):
    """
    Renders the page that says "Free Download" and gives the final file link.
    """
    paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    
    # URL to the actual file serving view
    file_download_url = reverse('shop:download_file', args=[paper.slug])
    
    context = {
        'paper': paper,
        'file_download_url': file_download_url
    }
    return render(request, 'shop/free_download_landing.html', context)


# ====================================================================
# 5. ACTUAL FILE DOWNLOAD VIEW
# ====================================================================

def download_file(request, paper_slug):
    """
    Serves the file directly to the user's browser.
    """
    paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    
    # Optional check: Block paid papers if someone finds this direct link
    if paper.is_paid:
        raise Http404("This file requires payment.")

    if not paper.pdf_file:
        raise Http404("This paper does not have an associated file for download.")

    try:
        # Get the absolute path to the file
        file_path = paper.pdf_file.path 
        file_handle = open(file_path, 'rb')
        
        # FileResponse handles streaming the file content efficiently
        response = FileResponse(
            file_handle, 
            as_attachment=True, 
            filename=os.path.basename(file_path)
        )
        return response
    
    except FileNotFoundError:
        raise Http404("The requested paper file was not found on the server.")
    except Exception as e:
        return render(request, 'shop/error.html', {'message': f"An unexpected error occurred during download: {e}"})


# ====================================================================
# 6. PAYMENT CALLBACK VIEW
# ====================================================================

def payment_callback(request):
    """
    Handles the user redirect after payment on the Paystack gateway.
    """
    reference = request.GET.get('reference')
    
    context = {
        'reference': reference,
    }
    return render(request, 'shop/callback_success.html', context)


# ====================================================================
# 7. PAYSTACK WEBHOOK HANDLER
# ====================================================================

@csrf_exempt
def paystack_webhook(request):
    """
    Handles POST requests from Paystack, verifies the payment, marks it as verified, 
    and triggers the SMS with the password.
    """
    if request.method != 'POST':
        return HttpResponse(status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if payload.get('event') == 'charge.success':
        reference = payload['data']['reference']
        
        try:
            payment = Payment.objects.get(ref=reference)
        except Payment.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Payment reference not found'}, status=400)

        # 4. Verify Payment with Paystack (Double Check)
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        verification_url = f"https://api.paystack.co/transaction/verify/{reference}"
        verification_response = requests.get(verification_url, headers=headers)
        verification_data = verification_response.json()

        if (verification_data['data']['status'] == 'success' and 
            verification_data['data']['amount'] == payment.amount_in_kobo()):
            
            # 5. Mark Payment as Verified and Send Fulfillment
            if not payment.verified:
                payment.verified = True
                payment.save()

                question_paper = payment.question_paper
                
                # Compose the SMS message
                message = f"Your password for {question_paper.title} is: {question_paper.password}. Thank you for your purchase from Insight Innovations!" 
                
                # Arkesel API Details
                arkesel_url = "https://sms.arkesel.com/api/v2/sms/send"
                arkesel_payload = {
                    "sender": "Insight Innovations", 
                    "message": message,
                    "recipients": [payment.phone_number],
                    "apiKey": settings.ARKESEL_API_KEY
                }

                # Send the SMS via Arkesel
                requests.post(arkesel_url, json=arkesel_payload)
                
                return JsonResponse({'status': 'success', 'message': 'Payment verified and password sent'}, status=200)
            
            return JsonResponse({'status': 'success', 'message': 'Payment already verified'}, status=200)

        return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)

    return JsonResponse({'status': 'success', 'message': 'Webhook received, but not a charge success event'}, status=200)


# ====================================================================
# 8. Placeholder Views (ADD CONTACT VIEW)
# ====================================================================

def profile(request):
    """Placeholder for My Profile view."""
    return render(request, 'shop/profile.html', {'page_title': 'My Profile'})

def purchase_history(request):
    """Placeholder for Purchase History view."""
    return render(request, 'shop/purchase_history.html', {'page_title': 'Purchase History'})

def login(request):
    """Placeholder for Login view."""
    return redirect('admin:login')

def logout(request):
    """Placeholder for Logout view."""
    return redirect('shop:class_list')

def register(request):
    """Placeholder for Register view."""
    return render(request, 'shop/register.html', {'page_title': 'Register'})


def contact_us(request):
    """
    Handles the contact form display and submission, and sends the message via email.
    """
    # === UPDATED IMPORT: send_mail is now imported at the top of the file ===
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            visitor_email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # 1. Compose the Email Content
            full_subject = f"[CONTACT FORM] {subject} - From: {name}"
            email_body = f"Message received from the website contact form.\n\n"
            email_body += f"Name: {name}\n"
            email_body += f"Email: {visitor_email}\n"
            email_body += f"Subject: {subject}\n\n"
            email_body += f"--- MESSAGE CONTENT ---\n{message}\n---------------------\n"
            
            try:
                # 2. Send Email to the Admin (Your Account)
                send_mail(
                    full_subject,
                    email_body,
                    settings.DEFAULT_FROM_EMAIL, # Sender (configured in settings.py)
                    ['darkosammy2@gmail.com'], # Admin Recipient (Your Email)
                    fail_silently=False,
                )
                
                # Optional: Send Confirmation to the Visitor (Good practice)
                send_mail(
                    f"Confirmation: We received your message",
                    f"Dear {name},\n\nThank you for reaching out to us. We have received your message regarding: '{subject}'. We will respond as soon as possible.\n\n---\nInsight Innovations Team",
                    settings.DEFAULT_FROM_EMAIL,
                    [visitor_email],
                    fail_silently=True,
                )
                
                context = {
                    'page_title': 'Message Sent',
                    'success': True,
                    'name': name
                }
                return render(request, 'shop/contact_us.html', context)

            except Exception as e:
                # Handle email sending errors (e.g., incorrect settings)
                print(f"Error sending contact email: {e}")
                # Re-display the form with an error message
                context = {
                    'page_title': 'Contact Us - Error',
                    'form': form,
                    'success': False,
                    'email_error': 'There was a server error sending your message. Please try again or call us.',
                    'phone': '+233542232515', 
                    'email': 'darkosammy2@gmail.com',
                    'location': 'Accra, Ghana'
                }
                return render(request, 'shop/contact_us.html', context)
    
    # Initial GET request or non-valid form submission
    else:
        form = ContactForm()
    
    # Context for displaying the form
    context = {
        'page_title': 'Contact Us',
        'form': form,
        'success': False,
        # Static Contact Details to display on the page
        'phone': '+233542232515', 
        'email': 'darkosammy2@gmail.com',
        'location': 'Accra, Ghana'
    }
    return render(request, 'shop/contact_us.html', context)