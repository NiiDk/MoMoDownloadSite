# shop/views.py (Replace the entire file content with this)

import json
import requests
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.urls import reverse
from django.db import models
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_POST
import logging
from datetime import datetime
import os
from .email_utils import EmailService # <--- CRITICAL NEW IMPORT

# Initialize logger
logger = logging.getLogger(__name__)

# ====================================================================
# 1. HIERARCHICAL LIST VIEWS (Navigation) - UNCHANGED
# ====================================================================

# 1.1. Homepage: List all Classes/Grades
def class_list(request):
    """
    Displays the top-level list of all available Classes (e.g., JHS 1).
    """
    classes = Classes.objects.all()
    context = {
        'classes': classes,
        'page_title': 'Select Your Class/Grade',
        'is_homepage': True
    }
    return render(request, 'shop/class_list.html', context)
    
# 1.2. Second Level: List all Terms for a Class
def term_list(request, class_slug):
    """
    Displays the list of terms (Term 1, 2, 3) available for the selected Class.
    """
    class_level = get_object_or_404(Classes, slug=class_slug)
    terms = class_level.terms.all()
    context = {
        'class_level': class_level,
        'terms': terms,
        'page_title': f'Select Term for {class_level.name}',
    }
    return render(request, 'shop/term_list.html', context)

# 1.3. Third Level: List all Subjects for a Term
def subject_list(request, class_slug, term_slug):
    """
    Displays the list of subjects available for the selected Class and Term.
    """
    class_level = get_object_or_404(Classes, slug=class_slug)
    term = get_object_or_404(Term, class_name=class_level, slug=term_slug) 
    
    subjects = Subject.objects.all().prefetch_related(
        models.Prefetch(
            'papers',
            queryset=QuestionPaper.objects.filter(
                class_level=class_level, 
                term=term
            ),
            to_attr='filtered_papers'
        )
    )

    context = {
        'class_level': class_level,
        'term': term,
        'subjects': subjects,
        'page_title': f'{class_level.name} {term.name} - Select Subject',
    }
    return render(request, 'shop/subject_list.html', context)
    
# 1.4. Final Level: Paper Detail/Buy Page
def paper_detail(request, class_slug, term_slug, subject_slug, paper_slug):
    """
    Displays the specific paper that the user can purchase (the product page).
    """
    paper = get_object_or_404(QuestionPaper, 
        class_level__slug=class_slug,
        term__slug=term_slug,
        subject__slug=subject_slug,
        slug=paper_slug
    )

    if paper.is_paid:
        button_url = reverse('shop:buy_paper', args=[paper.slug])
        button_text = "Buy Now & Get Password via SMS"
    else:
        button_url = reverse('shop:download_page', args=[paper.slug])
        button_text = "Free Download"
    
    context = {
        'paper': paper,
        'page_title': paper.title,
        'currency_code': settings.CURRENCY_CODE,
        'button_url': button_url,     
        'button_text': button_text    
    }
    return render(request, 'shop/paper_detail.html', context)


# ====================================================================
# 2. FORM DEFINITION - UNCHANGED
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

# Note: The original ContactForm is removed since the new contact form is AJAX-based 
# and handles validation in the view using standard Django/Python validation.


# ====================================================================
# 3. MAIN CONDITIONAL LOGIC & PAYMENT INITIATION - UNCHANGED
# ====================================================================

def initiate_payment_or_download(request, paper_slug):
    """
    Handles 'shop:buy_paper'. Checks the 'is_paid' flag:
    """
    try:
        paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    except Exception:
        return render(request, 'shop/error.html', {'message': 'The requested item was not found.'})

    # === CONDITIONAL LOGIC ===
    if not paper.is_paid:
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
# 4. FREE DOWNLOAD LANDING PAGE - UNCHANGED
# ====================================================================

def free_download_landing(request, paper_slug):
    """
    Renders the page that says "Free Download" and gives the final file link.
    """
    paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    
    file_download_url = reverse('shop:download_file', args=[paper.slug])
    
    context = {
        'paper': paper,
        'file_download_url': file_download_url
    }
    return render(request, 'shop/free_download_landing.html', context)


# ====================================================================
# 5. ACTUAL FILE DOWNLOAD VIEW - UNCHANGED
# ====================================================================

def download_file(request, paper_slug):
    """
    Serves the file directly to the user's browser.
    """
    paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    
    if paper.is_paid:
        raise Http404("This file requires payment.")

    if not paper.pdf_file:
        raise Http404("This paper does not have an associated file for download.")

    try:
        file_path = paper.pdf_file.path 
        file_handle = open(file_path, 'rb')
        
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
# 6. PAYMENT CALLBACK VIEW - UNCHANGED
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
# 7. PAYSTACK WEBHOOK HANDLER - UNCHANGED
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
# 8. CONTACT VIEWS (ROBUST ASYNC EMAIL)
# ====================================================================

def contact(request):
    """
    [GET request] Displays contact form page (renders the new contact.html template)
    """
    from django.conf import settings
    context = {
        'title': 'Contact Us',
        'admin_email': settings.EMAIL_HOST_USER,
    }
    return render(request, 'shop/contact.html', context)


@require_POST
@csrf_exempt 
def contact_view(request):
    """
    [POST request / AJAX Endpoint] Handle contact form submissions using EmailService.
    """
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()
        
        # 1. Validation
        if not all([name, email, subject, message]):
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
        
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({'success': False, 'error': 'Invalid email address'}, status=400)

        # 2. Log and Send
        logger.info(f"📨 Contact form submission from {name} <{email}>")
        
        # This function uses the non-blocking thread/timeout logic
        success, error = EmailService.send_contact_email(
            name=name,
            visitor_email=email,
            subject=subject,
            message=message
        )
        
        if success:
            return JsonResponse({'success': True, 'message': 'Your message has been sent successfully! We will be in touch shortly.'})
        else:
            logger.error(f"❌ Failed to send contact email: {error}. Check 'failed_emails.log'.")
            return JsonResponse({'success': False, 'error': f'Failed to send message. (Server Error: {error})'}, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid request data format'}, status=400)
    except Exception as e:
        logger.error(f"🔥 Unexpected error in contact_view: {str(e)}")
        return JsonResponse({'success': False, 'error': 'An unexpected server error occurred.'}, status=500)