import json
import requests
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db import models
from .models import Classes, Term, Subject, QuestionPaper, Payment
# Assuming you have models for authentication like 'UserProfile' if needed later

# ====================================================================
# 1. NEW HIERARCHICAL LIST VIEWS (Navigation)
# ====================================================================

# 1.1. Homepage: List all Classes/Grades
def class_list(request):
    """
    Displays the top-level list of all available Classes (e.g., JHS 1).
    This is the new homepage, aliased by the root URL '/'.
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
    
    # FIX APPLIED HERE: Used the correct related_name 'terms' defined in shop/models.py
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
    Optimized with prefetch_related for better performance.
    """
    class_level = get_object_or_404(Classes, slug=class_slug)
    # IMPORTANT: Assumes Term model has a ForeignKey to Classes named 'class_name'
    term = get_object_or_404(Term, class_name=class_level, slug=term_slug) 
    
    # Get all subjects with prefetched paper counts for this class/term
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
    # Fetch the specific Question Paper based on all slugs
    paper = get_object_or_404(QuestionPaper, 
        class_level__slug=class_slug,
        term__slug=term_slug,
        subject__slug=subject_slug,
        slug=paper_slug
    )

    context = {
        'paper': paper,
        'page_title': paper.title,
        'currency_code': settings.CURRENCY_CODE
    }
    return render(request, 'shop/paper_detail.html', context)


# ====================================================================
# 2. FORM DEFINITION 
# ====================================================================

class PurchaseForm(forms.Form):
    """Simple form for user input (email and phone number)"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    # Note: Paystack mobile money usually requires the format to include the country code (e.g., +23324xxxxxxx)
    phone_number = forms.CharField(
        label='Mobile Money Number (e.g., 024xxxxxxx)',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


# ====================================================================
# 3. PAYMENT INITIATION VIEW (MANDATORY: Resolves 'shop:buy_paper')
# ====================================================================

def initiate_payment(request, paper_slug):
    """
    Handles displaying the form and initiating the payment with Paystack.
    This view resolves the 'shop:buy_paper' URL reverse.
    """
    try:
        # 1. Get the Question Paper object using the slug
        paper = get_object_or_404(QuestionPaper, slug=paper_slug)
    except Exception:
        # Handles cases where the slug is valid but the object doesn't exist
        return render(request, 'shop/error.html', {'message': 'The requested item was not found.'})

    if request.method == 'POST':
        form = PurchaseForm(request.POST)

        if form.is_valid():
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']

            # 2. Create the local Payment record (unverified)
            payment = Payment.objects.create(
                question_paper=paper,
                email=email,
                phone_number=phone_number
            )
            
            # 3. Paystack API Call Setup
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
                # IMPORTANT: Use request.scheme for HTTPS on production
                "callback_url": f"{request.scheme}://{request.get_host()}{reverse('shop:payment_callback')}",
                "channels": ["mobile_money"],
            }
            
            # 4. Make the request to Paystack
            response = requests.post(url, headers=headers, data=json.dumps(data))
            response_data = response.json()

            if response.status_code == 200 and response_data.get('status'):
                # 5. Success: Redirect user to Paystack payment gateway
                return redirect(response_data['data']['authorization_url'])
            else:
                # 6. Failure: Show a generic error page with the message from Paystack
                print(f"Paystack Error: {response_data}") # Log error for debugging
                return render(request, 'shop/error.html', {'message': response_data.get('message', 'Could not initiate payment.')})
    
    # 7. Initial GET request: Display the form
    else:
        form = PurchaseForm()

    return render(request, 'shop/buy_paper.html', {'form': form, 'paper': paper})


# ====================================================================
# 4. PAYMENT CALLBACK VIEW
# ====================================================================

def payment_callback(request):
    """
    Handles the user redirect after payment on the Paystack gateway.
    """
    reference = request.GET.get('reference')
    
    # Optional: You can trigger payment verification here if you don't rely solely on the webhook
    
    context = {
        'reference': reference,
    }
    return render(request, 'shop/callback_success.html', context)


# ====================================================================
# 5. PAYSTACK WEBHOOK HANDLER
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
        # NOTE: For production, you MUST verify the signature (using request.headers.get('x-paystack-signature'))
        
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
                # BRAND NAME: Insight Innovations
                message = f"Your password for {question_paper.title} is: {question_paper.password}. Thank you for your purchase from Insight Innovations!" 
                
                # Arkesel API Details
                arkesel_url = "https://sms.arkesel.com/api/v2/sms/send"
                arkesel_payload = {
                    # SENDER ID: Insight Innovations
                    "sender": "Insight Innovations", 
                    "message": message,
                    "recipients": [payment.phone_number],
                    "apiKey": settings.ARKESEL_API_KEY
                }

                # Send the SMS via Arkesel
                requests.post(arkesel_url, json=arkesel_payload)
                
                # Success Response for Paystack (MUST be 200 OK)
                return JsonResponse({'status': 'success', 'message': 'Payment verified and password sent'}, status=200)
            
            # If payment was already verified (webhook sent twice)
            return JsonResponse({'status': 'success', 'message': 'Payment already verified'}, status=200)

        # If verification fails 
        return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)

    # Respond successfully to all other Paystack events
    return JsonResponse({'status': 'success', 'message': 'Webhook received, but not a charge success event'}, status=200)

# ====================================================================
# 6. Placeholder Views (Needed for base.html links)
# ====================================================================

# NOTE: These placeholder views are necessary because they are referenced in base.html
def profile(request):
    """Placeholder for My Profile view."""
    return render(request, 'shop/profile.html', {'page_title': 'My Profile'})

def purchase_history(request):
    """Placeholder for Purchase History view."""
    return render(request, 'shop/purchase_history.html', {'page_title': 'Purchase History'})

def login(request):
    """Placeholder for Login view."""
    return redirect('admin:login') # Example: Redirect to Django Admin login for simplicity

def logout(request):
    """Placeholder for Logout view."""
    # You will use Django's built-in logout function here
    return redirect('shop:class_list')

def register(request):
    """Placeholder for Register view."""
    return render(request, 'shop/register.html', {'page_title': 'Register'})