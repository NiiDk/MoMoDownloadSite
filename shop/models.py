# shop/models.py

from django.db import models
import uuid

class QuestionPaper(models.Model):  # <--- Check this class name
    title = models.CharField(max_length=200)
    # Price in Ghana Cedis (GHS)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    pdf_file = models.FileField(upload_to='questions_pdfs/')
    # The secure key the user will receive via SMS
    password = models.CharField(max_length=50) 

    def __str__(self):
        return self.title

class Payment(models.Model):  # <--- Check this class name
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    # Unique reference for Paystack
    ref = models.CharField(max_length=200, unique=True, default=uuid.uuid4)
    # The CRITICAL field - True only after MoMo webhook confirms payment
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def amount_in_kobo(self):
        """ Paystack expects the amount in the smallest currency unit (Pesewas/Kobo) """
        return int(self.question_paper.price * 100)

    def __str__(self):
        return f"Payment for {self.question_paper.title} - Verified: {self.verified}"