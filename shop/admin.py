# MoMoDownloadSite/shop/admin.py

from django.contrib import admin
from .models import QuestionPaper, Payment

# Register your models here.
admin.site.register(QuestionPaper)
admin.site.register(Payment)