# shop/admin.py

from django.contrib import admin
# CRITICAL CHANGE: Import all new models
from .models import Classes, Term, Subject, QuestionPaper, Payment 


# --- 1. Admin setup for Hierarchy Models ---

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    # Ensures the slug is automatically generated from the name as you type
    prepopulated_fields = {'slug': ('name',)} 

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    # Allows filtering by the Class/Grade
    list_filter = ['class_name'] 

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


# --- 2. Enhanced Admin setup for QuestionPaper ---

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    # Displays the new hierarchy fields in the list view
    list_display = ['title', 'price', 'class_level', 'term', 'subject', 'is_paid']
    # Allows filtering by the new hierarchy fields
    list_filter = ['class_level', 'term', 'subject', 'is_paid']
    prepopulated_fields = {'slug': ('title',)}
    # Allows searching by title or price
    search_fields = ['title', 'price']


# --- 3. Enhanced Admin setup for Payment ---

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    # Displays all critical payment details
    list_display = ['question_paper', 'email', 'phone_number', 'ref', 'verified', 'date_created']
    # Allows filtering by verification status and date
    list_filter = ['verified', 'date_created']
    # Allows searching by payment reference, email, or phone number
    search_fields = ['ref', 'email', 'phone_number']
    # Makes the verified field easy to toggle directly in the list
    list_editable = ['verified']