from django.contrib import admin
from .models import Classes, Term, Subject, QuestionPaper, Payment, DownloadHistory

@admin.register(Classes)
class ClassesAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order', 'get_paper_count']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['order']
    search_fields = ['name', 'description']
    
    def get_paper_count(self, obj):
        return obj.get_paper_count()
    get_paper_count.short_description = 'Papers'

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_name', 'slug', 'order', 'get_paper_count']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['class_name']
    list_editable = ['order']
    search_fields = ['name', 'class_name__name']
    
    def get_paper_count(self, obj):
        return obj.get_paper_count()
    get_paper_count.short_description = 'Papers'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'get_paper_count', 'icon']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    
    def get_paper_count(self, obj):
        return obj.get_paper_count()
    get_paper_count.short_description = 'Papers'

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'class_level', 'term', 'subject', 'year', 
        'exam_type', 'price', 'is_paid', 'is_available', 'views'
    ]
    list_filter = [
        'class_level', 'term', 'subject', 'year', 
        'exam_type', 'is_paid', 'is_available'
    ]
    search_fields = ['title', 'description']
    readonly_fields = ['slug', 'file_size', 'views', 'created_at', 'updated_at']
    list_editable = ['is_available', 'price']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Hierarchy', {
            'fields': ('class_level', 'term', 'subject')
        }),
        ('Paper Details', {
            'fields': ('year', 'exam_type', 'pages')
        }),
        ('Pricing & Status', {
            'fields': ('price', 'is_paid', 'is_available', 'password')
        }),
        ('File', {
            'fields': ('pdf_file', 'file_size')
        }),
        ('Statistics', {
            'fields': ('views', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Auto-generate title if not provided
        if not obj.title or obj.title.strip() == '':
            obj.title = f"{obj.subject.name} {obj.exam_type} {obj.year}"
        super().save_model(request, obj, form, change)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['ref_short', 'question_paper', 'email', 'phone_number', 'verified', 'date_created']
    list_filter = ['verified', 'date_created']
    search_fields = ['ref', 'email', 'phone_number', 'question_paper__title']
    list_editable = ['verified']
    readonly_fields = ['ref', 'date_created']
    
    def ref_short(self, obj):
        return f"#{obj.ref[:8]}..."
    ref_short.short_description = 'Reference'

@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ['paper', 'user_email', 'downloaded_at', 'ip_address']
    list_filter = ['downloaded_at']
    search_fields = ['user_email', 'paper__title']
    readonly_fields = ['downloaded_at']