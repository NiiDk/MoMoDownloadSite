from django.db import models
from django.urls import reverse
import uuid
from django.utils import timezone

# --- 1. Class (Grade) Model ---
class Classes(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., JHS 1, Basic 7")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0, help_text="Order for display")

    class Meta:
        verbose_name = 'Class (Grade)'
        verbose_name_plural = 'Classes (Grades)'
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:term_list', args=[self.slug])

    def get_paper_count(self):
        """Get total number of papers for this class"""
        return self.papers.count()

# --- 2. Term Model ---
class Term(models.Model):
    class_name = models.ForeignKey(Classes, related_name='terms', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, help_text="e.g., Term 1, Term 2")
    slug = models.SlugField(max_length=50)
    order = models.IntegerField(default=0, help_text="Order for display")

    class Meta:
        verbose_name_plural = 'Terms'
        unique_together = ('class_name', 'slug')
        ordering = ('order', 'name')

    def __str__(self):
        return f"{self.class_name.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('shop:subject_list', args=[self.class_name.slug, self.slug])

    def get_paper_count(self):
        """Get total number of papers for this term"""
        return self.papers.count()

# --- 3. Subject Model ---
class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")

    class Meta:
        verbose_name_plural = 'Subjects'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_paper_count(self):
        """Get total number of papers for this subject"""
        return self.papers.count()

# --- 4. QuestionPaper Model (Updated) ---
class QuestionPaper(models.Model):
    # Core Information
    title = models.CharField(max_length=200)
    
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
    
    # File and pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_file = models.FileField(upload_to='questions_pdfs/%Y/%m/%d/')
    password = models.CharField(max_length=50)
    
    # Status flags
    is_paid = models.BooleanField(default=True, help_text="Is this a paid paper or a free sample?")
    is_available = models.BooleanField(default=True, help_text="Is this paper available for purchase?")
    
    # File information
    file_size = models.CharField(max_length=20, blank=True, editable=False)
    pages = models.IntegerField(default=1, help_text="Number of pages")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0, help_text="Number of times viewed")
    
    class Meta:
        ordering = ('-year', 'term__order', 'subject__name', 'title')
        verbose_name = 'Question Paper'
        verbose_name_plural = 'Question Papers'

    def __str__(self):
        return f"{self.class_level.name} - {self.term.name} - {self.subject.name} - {self.title} ({self.year})"

    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug or self.slug == str(uuid.uuid4()):
            base_slug = f"{self.class_level.slug}-{self.term.slug}-{self.subject.slug}-{self.year}-{self.exam_type}"
            self.slug = base_slug
            counter = 1
            while QuestionPaper.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        # Calculate file size
        if self.pdf_file:
            size_bytes = self.pdf_file.size
            if size_bytes < 1024:
                self.file_size = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                self.file_size = f"{size_bytes / 1024:.1f} KB"
            else:
                self.file_size = f"{size_bytes / (1024 * 1024):.1f} MB"
        
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('shop:paper_detail', 
                       args=[self.class_level.slug, self.term.slug, self.subject.slug, self.slug])

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

    def get_display_title(self):
        """Get formatted title for display"""
        return f"{self.title} ({self.year} {self.get_exam_type_display()})"

# --- 5. Payment Model (Kept) ---
class Payment(models.Model):
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='payments')
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    ref = models.CharField(max_length=200, unique=True, default=uuid.uuid4)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date_created',)
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def amount_in_kobo(self):
        return int(self.question_paper.price * 100)

    def __str__(self):
        return f"Payment #{self.ref[:8]} - {self.question_paper.title}"

# --- 6. NEW: Paper Download History ---
class DownloadHistory(models.Model):
    paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE, related_name='downloads')
    user_email = models.EmailField()
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    
    class Meta:
        ordering = ('-downloaded_at',)
        verbose_name = 'Download History'
        verbose_name_plural = 'Download Histories'
    
    def __str__(self):
        return f"{self.user_email} downloaded {self.paper.title}"