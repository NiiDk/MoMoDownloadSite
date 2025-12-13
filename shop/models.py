# shop/models.py

from django.db import models
from django.urls import reverse
import uuid
from django.utils import timezone
from cloudinary.models import CloudinaryField  # Add CloudinaryField

# --- 1. Class (Grade) Model ---
class Classes(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., JHS 1, Basic 7")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Class (Grade)'
        verbose_name_plural = 'Classes (Grades)'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:term_list', args=[self.slug])

    def get_paper_count(self):
        return self.papers.count()


# --- 2. Term Model ---
class Term(models.Model):
    class_name = models.ForeignKey(Classes, related_name='terms', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, help_text="e.g., Term 1, Term 2")
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name_plural = 'Terms'
        unique_together = ('class_name', 'slug')
        ordering = ('name',)

    def __str__(self):
        return f"{self.class_name.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('shop:subject_list', args=[self.class_name.slug, self.slug])

    def get_paper_count(self):
        return self.papers.count()


# --- 3. Subject Model ---
class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Subjects'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_paper_count(self):
        return self.papers.count()


# --- 4. QuestionPaper Model (UPDATED WITH CLOUDINARY) ---
class QuestionPaper(models.Model):
    # Core Information
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, help_text="Description of the paper")
    
    # Hierarchy Relationships
    class_level = models.ForeignKey(Classes, related_name='papers', on_delete=models.PROTECT)
    term = models.ForeignKey(Term, related_name='papers', on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, related_name='papers', on_delete=models.PROTECT)
    
    # Unique identifier
    slug = models.SlugField(max_length=200, unique=True, default=uuid.uuid4)
    
    # Paper details
    year = models.IntegerField(
        default=timezone.now().year,
        help_text="Year the paper was administered"
    )
    exam_type = models.CharField(
        max_length=50,
        choices=[
            ('midterm', 'Mid-Term Exam'),
            ('endterm', 'End-Term Exam'),
            ('cat', 'CAT (Continuous Assessment Test)'),
            ('assignment', 'Assignment'),
            ('final', 'Final Exam'),
            ('mock', 'Mock Exam'),
            ('others', 'Others'),
        ],
        default='endterm'
    )
    
    # File and pricing - UPDATED WITH CLOUDINARY
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Replace FileField with CloudinaryField
    pdf_file = CloudinaryField(
        'raw',  # 'raw' for PDF files
        folder='question_papers/',  # Organize in Cloudinary folder
        resource_type='raw',  # Explicitly set to raw for PDFs
        blank=False,
        null=False,
        help_text="Upload PDF question paper"
    )
    password = models.CharField(max_length=50, blank=True)  # Made optional
    
    # Status flags
    is_paid = models.BooleanField(default=True, help_text="Is this a paid paper or a free sample?")
    is_available = models.BooleanField(default=True, help_text="Is this paper available for purchase?")
    
    # File information - Cloudinary provides this automatically
    file_size = models.CharField(max_length=20, blank=True, editable=False)
    pages = models.IntegerField(default=1, help_text="Number of pages")
    
    # Preview image (optional) - USING CLOUDINARY
    preview_image = CloudinaryField(
        'image',
        folder='question_paper_previews/',
        null=True,
        blank=True,
        help_text="Preview/sample image of the question paper"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0, help_text="Number of times viewed")
    
    # Cloudinary public ID for easy reference
    cloudinary_public_id = models.CharField(max_length=300, blank=True, editable=False)
    
    class Meta:
        ordering = ('class_level', 'term', 'subject', 'title')
        verbose_name = 'Question Paper'
        verbose_name_plural = 'Question Papers'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['class_level', 'term', 'subject']),
            models.Index(fields=['is_available', 'is_paid']),
        ]

    def __str__(self):
        return f"{self.class_level.name} - {self.term.name} - {self.subject.name} ({self.title})"

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug or self.slug == str(uuid.uuid4()):
            import re
            from django.utils.text import slugify
            
            base_slug = slugify(f"{self.class_level.name} {self.term.name} {self.subject.name} {self.title}")
            self.slug = base_slug
            counter = 1
            while QuestionPaper.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Store Cloudinary public ID if available
        if self.pdf_file and hasattr(self.pdf_file, 'public_id'):
            self.cloudinary_public_id = self.pdf_file.public_id
        
        # Set default password if not provided
        if not self.password and self.is_paid:
            self.password = f"INSIGHT_{uuid.uuid4().hex[:8].upper()}"
        
        # Update file size for Cloudinary (if we want to track it)
        if self.pdf_file and not self.file_size:
            try:
                # Cloudinary stores file size in bytes
                if hasattr(self.pdf_file, 'metadata') and 'bytes' in self.pdf_file.metadata:
                    size_bytes = self.pdf_file.metadata['bytes']
                    if size_bytes < 1024:
                        self.file_size = f"{size_bytes} B"
                    elif size_bytes < 1024 * 1024:
                        self.file_size = f"{size_bytes / 1024:.1f} KB"
                    else:
                        self.file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
            except:
                pass
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse(
            'shop:paper_detail',
            args=[self.class_level.slug, self.term.slug, self.subject.slug, self.slug]
        )

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_display_title(self):
        return self.title
    
    # Cloudinary-specific methods
    def get_pdf_url(self):
        """Get Cloudinary URL for the PDF file"""
        if self.pdf_file:
            return self.pdf_file.url
        return None
    
    def get_secure_pdf_url(self):
        """Get secure Cloudinary URL for the PDF"""
        if self.pdf_file:
            # Force HTTPS and add security transformations if needed
            return str(self.pdf_file.url).replace('http://', 'https://')
        return None
    
    def get_preview_image_url(self):
        """Get preview image URL with transformations"""
        if self.preview_image:
            return self.preview_image.url
        return None
    
    def generate_thumbnail(self, width=300, height=400):
        """Generate a thumbnail URL from preview image"""
        if self.preview_image:
            from cloudinary import CloudinaryImage
            img = CloudinaryImage(self.preview_image.public_id)
            return img.build_url(width=width, height=height, crop="fill")
        return None
    
    @property
    def file_name(self):
        """Extract file name from Cloudinary URL"""
        if self.pdf_file and hasattr(self.pdf_file, 'public_id'):
            return self.pdf_file.public_id.split('/')[-1]
        return "question_paper.pdf"
    
    @property
    def is_free(self):
        """Check if paper is free"""
        return self.price == 0 or not self.is_paid


# --- 5. Payment Model ---
class Payment(models.Model):
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    ref = models.CharField(max_length=200, unique=True, default=uuid.uuid4)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Payment details
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, default='paystack')
    transaction_id = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ('-date_created',)
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        indexes = [
            models.Index(fields=['ref']),
            models.Index(fields=['email', 'verified']),
        ]

    def amount_in_pesewas(self):
        return int(self.question_paper.price * 100)

    def __str__(self):
        return f"Payment for {self.question_paper.title} - Verified: {self.verified}"
    
    def mark_as_verified(self, transaction_id=None, amount=None):
        """Mark payment as verified"""
        self.verified = True
        if transaction_id:
            self.transaction_id = transaction_id
        if amount:
            self.amount_paid = amount
        self.save()
    
    @property
    def download_url(self):
        """Get download URL after payment verification"""
        if self.verified and self.question_paper.pdf_file:
            return self.question_paper.get_pdf_url()
        return None


# --- 6. Paper Download History ---
class DownloadHistory(models.Model):
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='downloads')
    user_email = models.EmailField()
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='downloads')
    user_agent = models.TextField(blank=True)  # Browser info
    
    class Meta:
        ordering = ('-downloaded_at',)
        verbose_name = 'Download History'
        verbose_name_plural = 'Download Histories'
        indexes = [
            models.Index(fields=['paper', 'downloaded_at']),
            models.Index(fields=['user_email']),
        ]
    
    def __str__(self):
        return f"{self.user_email} downloaded {self.paper.title}"
    
    @classmethod
    def log_download(cls, paper, email, request=None, payment=None):
        """Helper method to log a download"""
        download = cls(
            paper=paper,
            user_email=email,
            payment=payment
        )
        
        if request:
            download.ip_address = request.META.get('REMOTE_ADDR')
            download.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        download.save()
        return download


# --- 7. FREE SAMPLE Model (Optional but recommended) ---
class FreeSample(models.Model):
    """Free samples to attract customers"""
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, limit_choices_to={'is_paid': True})
    sample_pdf = CloudinaryField(
        'raw',
        folder='free_samples/',
        resource_type='raw',
        help_text="Sample PDF (first few pages only)"
    )
    description = models.TextField(help_text="What's included in this sample")
    downloads = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Free Sample'
        verbose_name_plural = 'Free Samples'
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Free sample of {self.question_paper.title}"
    
    def increment_downloads(self):
        self.downloads += 1
        self.save(update_fields=['downloads'])