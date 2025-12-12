# shop/admin.py

from django.contrib import admin
from .models import Classes, Term, Subject, QuestionPaper, Payment
# Comment out DownloadHistory for now since it might not exist yet
# from .models import DownloadHistory

# --- 1. Admin setup for Hierarchy Models ---

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_paper_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    def get_paper_count(self, obj):
        return obj.papers.count()
    get_paper_count.short_description = 'Papers'

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'name', 'slug', 'get_paper_count']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['class_name']
    search_fields = ['name', 'class_name__name']
    
    def get_paper_count(self, obj):
        return obj.papers.count()
    get_paper_count.short_description = 'Papers'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_paper_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    
    def get_paper_count(self, obj):
        return obj.papers.count()
    get_paper_count.short_description = 'Papers'

# --- 2. Enhanced Admin setup for QuestionPaper ---

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    # Simple list display with only fields that exist
    list_display = ['title', 'class_level', 'term', 'subject', 'price', 'is_paid']
    list_filter = ['class_level', 'term', 'subject', 'is_paid']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'price']
    
    # Only include fields that actually exist in your model
    # Remove readonly_fields and list_editable for now to avoid errors
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'class_level', 'term', 'subject')
        }),
        ('Paper Details', {
            'fields': ('year', 'exam_type', 'pages'),
            'classes': ('collapse',)  # Make collapsible
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_paid', 'password')
        }),
        ('File', {
            'fields': ('pdf_file',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Auto-generate title if not provided
        if not obj.title or obj.title.strip() == '':
            obj.title = f"{obj.subject.name} {obj.get_exam_type_display()} {obj.year}"
        super().save_model(request, obj, form, change)

# --- 3. Enhanced Admin setup for Payment ---

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['question_paper', 'email', 'phone_number', 'ref_short', 'verified', 'date_created']
    list_filter = ['verified', 'date_created']
    search_fields = ['ref', 'email', 'phone_number', 'question_paper__title']
    list_editable = ['verified']
    readonly_fields = ['ref', 'date_created']
    
    def ref_short(self, obj):
        return f"#{obj.ref[:8]}..."
    ref_short.short_description = 'Reference'

# --- 4. Comment out DownloadHistory for now ---
# @admin.register(DownloadHistory)
# class DownloadHistoryAdmin(admin.ModelAdmin):
#     list_display = ['paper', 'user_email', 'downloaded_at', 'ip_address']
#     list_filter = ['downloaded_at']
#     search_fields = ['user_email', 'paper__title']
#     readonly_fields = ['downloaded_at']