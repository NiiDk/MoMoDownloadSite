# shop/models.py

from django.db import models
from django.urls import reverse # <-- New Import: Needed for get_absolute_url
import uuid

# --- 1. Class (Grade) Model ---
class Classes(models.Model):
    name = models.CharField(max_length=100, help_text="e.g., JHS 1, Basic 7")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Class (Grade)'
        verbose_name_plural = 'Classes (Grades)'
        ordering = ('name',)  # Keep ordering by name only

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # URL for viewing all terms within this class
        return reverse('shop:term_list', args=[self.slug])

# --- 2. Term Model ---
class Term(models.Model):
    class_name = models.ForeignKey(Classes, related_name='terms', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, help_text="e.g., Term 1, Term 2")
    slug = models.SlugField(max_length=50)

    class Meta:
        verbose_name_plural = 'Terms'
        unique_together = ('class_name', 'slug') # Ensures a class doesn't have two Terms with the same slug
        ordering = ('name',)

    def __str__(self):
        return f"{self.class_name.name} - {self.name}"

    def get_absolute_url(self):
        # URL for viewing all subjects within this term
        return reverse('shop:subject_list', args=[self.class_name.slug, self.slug])

# --- 3. Subject Model ---
class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Subjects'
        ordering = ('name',)

    def __str__(self):
        return self.name

# --- 4. QuestionPaper Model (Updated) ---
class QuestionPaper(models.Model):
    # Old Fields (Kept)
    title = models.CharField(max_length=200)
    
    # New Foreign Keys to the Hierarchy (CRITICAL CHANGES)
    class_level = models.ForeignKey(Classes, related_name='papers', on_delete=models.PROTECT)
    term = models.ForeignKey(Term, related_name='papers', on_delete=models.PROTECT)
    subject = models.ForeignKey(Subject, related_name='papers', on_delete=models.PROTECT)
    
    # New Field: slug is necessary for unique URLs
    slug = models.SlugField(max_length=200, unique=True, default=uuid.uuid4)

    price = models.DecimalField(max_digits=10, decimal_places=2) 
    pdf_file = models.FileField(upload_to='questions_pdfs/')
    password = models.CharField(max_length=50) 
    
    # Optional: is_paid flag for easy filtering in admin/views
    is_paid = models.BooleanField(default=True, help_text="Is this a paid paper or a free sample?")


    class Meta:
        ordering = ('class_level', 'term', 'subject', 'title')

    def __str__(self):
        return f"{self.class_level.name} - {self.term.name} - {self.subject.name} ({self.title})"

    def get_absolute_url(self):
        # URL for buying the specific paper
        return reverse('shop:paper_detail', 
                       args=[self.class_level.slug, self.term.slug, self.subject.slug, self.slug])


# --- 5. Payment Model (Kept) ---
class Payment(models.Model):
    question_paper = models.ForeignKey(QuestionPaper, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    ref = models.CharField(max_length=200, unique=True, default=uuid.uuid4)
    verified = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-date_created',) # Show newest payments first

    def amount_in_kobo(self):
        """ Paystack expects the amount in the smallest currency unit (Pesewas/Kobo) """
        return int(self.question_paper.price * 100)

    def __str__(self):
        return f"Payment for {self.question_paper.title} - Verified: {self.verified}"