# MoMoDownloadSite/shop/views.py

import json
import requests
from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from .models import QuestionPaper, Payment

# MoMoDownloadSite/shop/views.py

# ... existing imports ...

# MoMoDownloadSite/shop/views.py

# ... existing code ...

# ====================================================================
# 0. ITEM LIST VIEW (The Homepage for all users)
# ====================================================================

def paper_list(request):
    """
    Displays a list of all available question papers for users to select.
    """
    # Fetches all QuestionPaper objects from the database
    papers = QuestionPaper.objects.all()
    context = {
        'papers': papers
    }
    # Renders the new item listing template
    return render(request, 'paper_list.html', context)

# ====================================================================
# 1. FORM DEFINITION
# ... rest of the file ...
# ====================================================================
# 1. FORM DEFINITION
# ====================================================================

class PurchaseForm(forms.Form):
    """Simple form for user input (email and phone number)"""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone_number = forms.CharField(
        label='Mobile Money Number (e.g., 055xxxxxxx)',
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )


# ====================================================================
# 2. PAYMENT INITIATION VIEW (The /buy/1/ page)
# ====================================================================

def initiate_payment(request, paper_id):
    """
    Handles displaying the form and initiating the payment with Paystack.
    """
    try:
        # 1. Get the Question Paper object
        paper = get_object_or_404(QuestionPaper, id=paper_id)
    except Exception:
        return render(request, 'error.html', {'message': 'The requested item was not found.'})

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
            
            # Prepare data for Paystack. Amount must be in the smallest currency unit (Pesewas/Kobo)
            data = {
                "email": email,
                "amount": payment.amount_in_kobo(),  # e.g., 10.00 GHS * 100 = 1000
                "currency": settings.CURRENCY_CODE,
                "reference": str(payment.ref), # Converted UUID to string for JSON serialization
                "callback_url": f"http://{request.get_host()}/payment/callback/", # Placeholder for user redirect
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
                return render(request, 'error.html', {'message': response_data.get('message', 'Could not initiate payment.')})
    
    # 7. Initial GET request: Display the form
    else:
        form = PurchaseForm()

    return render(request, 'buy_paper.html', {'form': form, 'paper': paper})


# ====================================================================
# 2.5. PAYMENT CALLBACK VIEW (The /payment/callback/ page)
# ====================================================================

def payment_callback(request):
    """
    Handles the user redirect after payment on the Paystack gateway.
    It doesn't verify the payment here; verification happens via the webhook.
    """
    # Paystack adds trxref and reference to the GET request.
    reference = request.GET.get('reference')
    
    # We don't need to do much here, just show a friendly message.
    # The actual fulfillment (verification and SMS) is handled by the webhook.
    
    context = {
        'reference': reference,
    }
    return render(request, 'callback_success.html', context)


# ====================================================================
# 3. PAYSTACK WEBHOOK HANDLER (The /webhooks/paystack/ page)
# ====================================================================

@csrf_exempt
def paystack_webhook(request):
    """
    Handles POST requests from Paystack, verifies the payment, marks it as verified, 
    and triggers the SMS with the password.
    """
    # 1. Check for POST Request (Webhooks are POSTs)
    if request.method != 'POST':
        return HttpResponse(status=400)

    # 2. Read the payload
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    # 3. Process successful transaction events
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

        # Check if Paystack confirms success AND the amount matches what we expected
        if (verification_data['data']['status'] == 'success' and 
            verification_data['data']['amount'] == payment.amount_in_kobo()):
            
            # 5. Mark Payment as Verified and Send Fulfillment
            if not payment.verified:
                payment.verified = True
                payment.save()

                # Get the password for the purchased paper
                question_paper = payment.question_paper
                
                # Compose the SMS message
                message = f"Your password for {question_paper.title} is: {question_paper.password}. Thank you for your purchase!"
                
                # Arkesel API Details
                arkesel_url = "https://sms.arkesel.com/api/v2/sms/send"
                arkesel_payload = {
                    "sender": "MoMoSite", 
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

        # If verification fails (e.g., amount mismatch or Paystack says failed)
        return JsonResponse({'status': 'error', 'message': 'Payment verification failed'}, status=400)

    # Respond successfully to all other Paystack events
    return JsonResponse({'status': 'success', 'message': 'Webhook received, but not a charge success event'}, status=200)

    # MoMoDownloadSite/shop/views.py (Add this function)

def paper_list(request):
    """
    Displays a list of all available question papers for users to select.
    """
    papers = QuestionPaper.objects.all()
    context = {
        'papers': papers
    }
    return render(request, 'paper_list.html', context)