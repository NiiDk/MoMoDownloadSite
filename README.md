# Insight Innovations - Question Paper Download Platform

A Django-based web application for managing and selling digital educational question papers. Students can browse papers by class, term, and subject, and make secure payments via Paystack to access premium content.

## Features

- **Hierarchical Browsing**: Navigate by Class → Term → Subject → Paper
- **Search & Filter**: Find papers by title, subject, class, year, or exam type
- **Payment Integration**: Secure payments via Paystack with SMS delivery of passwords
- **Download Tracking**: Monitor downloads with IP, email, and timestamp logging
- **Admin Dashboard**: Comprehensive Django admin interface for managing papers and payments
- **Free & Paid Content**: Support for both free samples and premium paid papers
- **Responsive Design**: Mobile-optimized interface with Bootstrap 5
- **Email Notifications**: Automated confirmation emails for contact submissions

## Project Structure

```
MoMoDownloadSite/
├── InsightInnovations/          # Django project settings
│   ├── settings.py              # Project configuration
│   ├── urls.py                  # Root URL routing
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
├── shop/                        # Main Django app
│   ├── models.py                # Database models (Classes, Terms, Subjects, Papers, Payments, etc.)
│   ├── views.py                 # View functions (hierarchical browsing, payments, downloads)
│   ├── urls.py                  # App URL routing
│   ├── admin.py                 # Django admin configuration
│   ├── forms.py                 # Form definitions (PurchaseForm, ContactForm)
│   ├── context_processors.py    # Template context processors
│   ├── migrations/              # Database migrations
│   ├── templates/shop/          # HTML templates
│   │   ├── includes/            # Template includes (header, footer, cards)
│   │   ├── email/               # Email templates
│   │   ├── base.html            # Base template
│   │   ├── class_list.html      # Class/Grade selection
│   │   ├── term_list.html       # Term selection
│   │   ├── subject_list.html    # Subject selection
│   │   ├── paper_detail.html    # Paper detail view
│   │   ├── buy_paper.html       # Payment form
│   │   ├── callback_success.html# Payment success page
│   │   ├── search_results.html  # Search results
│   │   ├── about.html           # About page
│   │   ├── faq.html             # FAQ page
│   │   ├── contact_us.html      # Contact form
│   │   └── ... (other pages)
│   └── __pycache__/
├── templates/                   # Project-level templates
│   └── base.html                # Main base template with responsive CSS
├── staticfiles/                 # Collected static files
├── media/                       # User-uploaded files (PDFs, etc.)
│   ├── question_papers/         # Question paper PDFs
│   └── free_samples/            # Free sample PDFs
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── Procfile                     # Procfile for deployment (Render)
└── README.md                    # This file

```

## Database Models

### Core Hierarchy Models
- **Classes**: Grade levels (e.g., JHS 1, Basic 7)
- **Term**: Academic terms (e.g., Term 1, Term 2)
- **Subject**: School subjects (e.g., Mathematics, English)

### Paper & Sales Models
- **QuestionPaper**: The main paper entity with:
  - Hierarchical relationships (class, term, subject)
  - Pricing and availability flags
  - PDF file storage (local FileSystemStorage)
  - View tracking and metadata
  - Auto-generated slugs and unique references
  
- **Payment**: Transaction records with:
  - Paystack integration
  - Verification status
  - Amount tracking
  - Customer email and phone
  
- **DownloadHistory**: Download tracking with:
  - IP address logging
  - User agent tracking
  - Download timestamp
  - Associated payment reference
  
- **FreeSample**: Free sample papers with:
  - Download counter
  - One-to-one relationship with QuestionPaper

## Setup & Installation

### Prerequisites
- Python 3.8+
- pip
- SQLite3 (included with Python)

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd MoMoDownloadSite
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** with required environment variables:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   
   # Payment & SMS APIs
   PAYSTACK_PUBLIC_KEY=your-paystack-public-key
   PAYSTACK_SECRET_KEY=your-paystack-secret-key
   ARKESEL_API_KEY=your-arkesel-api-key
   CURRENCY_CODE=GHS
   
   # Email Configuration
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   
   # Deployment
   RENDER_EXTERNAL_HOSTNAME=your-render-domain.onrender.com
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser** (admin account):
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files** (for production):
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` in your browser.

## Usage

### For Users
1. Navigate to the homepage to browse classes
2. Select a class → term → subject to view available papers
3. Click on a paper to view details
4. For free papers: Click "Free Download"
5. For paid papers: Click "Buy Now", enter email/phone, and complete Paystack payment
6. Password will be sent via SMS (via Arkesel)

### For Admins
1. Go to `http://127.0.0.1:8000/admin/`
2. Login with superuser credentials
3. Manage:
   - **Question Papers**: Create, edit, delete papers; view stats
   - **Payments**: Track and verify transactions
   - **Download History**: Monitor user downloads
   - **Classes/Terms/Subjects**: Manage the hierarchy

## Key Features Explained

### Hierarchical Browsing
Users navigate through a structured hierarchy for intuitive paper discovery:
- All Classes → Selected Class → All Terms → Selected Term → All Subjects → Papers for Subject

### Payment Flow
1. User selects a paid paper and enters email/phone
2. System creates an unverified Payment record
3. Redirects to Paystack payment gateway
4. After payment, Paystack webhook verifies transaction
5. Auto-generated password sent via Arkesel SMS
6. User can download paper with reference number

### Download Tracking
Every download logs:
- Paper ID
- User email
- IP address
- User agent (browser info)
- Download timestamp
- Associated payment (if applicable)

### File Storage
- **Local FileSystemStorage**: PDFs stored in `media/question_papers/`
- **URL Access**: `/media/question_papers/<filename.pdf>`
- **No external dependencies** (previously used Cloudinary, now simplified)

## API Endpoints

### Payment & Download APIs
- `POST /api/track-download/<slug>/` — Track a download
- `POST /api/resend-password/<ref>/` — Resend password SMS
- `GET /payment/status/<reference>/` — Check payment status
- `POST /payment/callback/` — Paystack callback handler
- `POST /webhooks/paystack/` — Paystack webhook endpoint

### Hierarchical Views
- `GET /` — List all classes
- `GET /<class_slug>/` — List terms for class
- `GET /<class_slug>/<term_slug>/` — List subjects for term
- `GET /<class_slug>/<term_slug>/<subject_slug>/list/` — List papers for subject
- `GET /<class_slug>/<term_slug>/<subject_slug>/<paper_slug>/` — Paper detail

### Search & Browse
- `GET /search/?q=<query>` — Search papers
- `GET /papers/` — All papers
- `GET /papers/year/<year>/` — Papers by year
- `GET /papers/type/<exam_type>/` — Papers by exam type

## Configuration Notes

### Settings (`InsightInnovations/settings.py`)
- **Database**: SQLite3 (db.sqlite3)
- **File Storage**: FileSystemStorage (local media folder)
- **Static Files**: Handled by WhiteNoise for production
- **Email**: SMTP (Gmail or custom)
- **Security**: CSRF protection, secure cookies in production

### Models Updates
Recent improvements:
- Auto-generated Payment references (UUID-based)
- Improved slug generation with fallback UUID
- `Payment.mark_as_verified()` method for marking payments verified
- `DownloadHistory.log_download()` classmethod for logging downloads
- Free sample download counter integration

### Responsive Design
- Mobile optimization with Bootstrap 5
- Compact card sizing for phones (max-width: 576px)
- Responsive navbar with offcanvas drawer
- Touch-friendly buttons and forms

## Deployment

### Render.com (Recommended)
1. Push repository to GitHub
2. Connect GitHub repo to Render
3. Set environment variables in Render dashboard
4. Deploy:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   ```

### Heroku (Legacy)
See Procfile configuration for reference.

## Troubleshooting

### Common Issues

**"Secret key not found"**
- Ensure `.env` file exists with `SECRET_KEY` set
- Or set environment variable: `export SECRET_KEY=your-key`

**"Payment not verified"**
- Check Paystack API keys in settings
- Verify webhook endpoint is accessible
- Check payment status in admin

**"SMS not sent"**
- Verify ARKESEL_API_KEY in settings
- Check phone number format (should include country code)
- Check Arkesel account balance

**"PDF not found for download"**
- Verify `pdf_file` field is set on QuestionPaper
- Check file exists in `media/question_papers/`
- Verify MEDIA_ROOT and MEDIA_URL in settings

## Technologies Used

- **Framework**: Django 4.2+
- **Frontend**: Bootstrap 5, Font Awesome 6, JavaScript
- **Database**: SQLite3
- **Payment**: Paystack API
- **SMS**: Arkesel API
- **Storage**: Local FileSystemStorage
- **Deployment**: Render.com

## Contact & Support

- **Email**: darkosammy2@gmail.com
- **Phone**: +233 542 232 515
- **Location**: Accra, Ghana

## License

This project is proprietary and not available for redistribution without permission.

---

**Last Updated**: December 14, 2025
