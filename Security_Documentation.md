# Django LibraryProject - Security Implementation

A secure Django application implementing comprehensive security measures to protect against common web vulnerabilities including XSS, CSRF, SQL injection, and clickjacking attacks.

## Security Features Implemented

### 1. Secure Settings Configuration

**Production Security Settings:**

- `DEBUG = False` in production to prevent information disclosure
- `SECURE_BROWSER_XSS_FILTER = True` - Browser XSS protection
- `X_FRAME_OPTIONS = 'DENY'` - Clickjacking prevention
- `SECURE_CONTENT_TYPE_NOSNIFF = True` - MIME-type sniffing protection
- `CSRF_COOKIE_SECURE = True` - HTTPS-only CSRF cookies
- `SESSION_COOKIE_SECURE = True` - HTTPS-only session cookies
- `SECURE_HSTS_SECONDS = 31536000` - HTTP Strict Transport Security

**Additional Security Headers:**

- `CSRF_COOKIE_HTTPONLY = True` - Prevents JavaScript access to CSRF token
- `SESSION_COOKIE_HTTPONLY = True` - Prevents JavaScript access to sessions
- `SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'`
- Enhanced password validation with 12-character minimum length

### 2. CSRF Protection

**Implementation:**

- `@csrf_protect` decorator on all form-handling views
- `{% csrf_token %}` tags in all form templates
- CSRF middleware properly configured
- CSRF cookies secured with HTTPOnly and Secure flags

**Protection Against:**

- Cross-Site Request Forgery attacks
- Unauthorized form submissions from external sites

### 3. SQL Injection Prevention

**Secure Data Access Patterns:**

- Django ORM used exclusively (no raw SQL queries)
- `get_object_or_404()` for safe object retrieval
- Parameterized queries through Django's Q objects
- Input validation using Django forms and validators
- `validate_integer()` for numeric inputs

**Search Functionality:**

```python
# SECURE: Using Django ORM Q objects
books = books.filter(
    Q(title__icontains=query) | Q(author__icontains=query)
).distinct()
```

### 4. Content Security Policy (CSP)

**CSP Headers Configured:**

- `CSP_DEFAULT_SRC = ("'self'",)` - Restrict resource loading to same origin
- `CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")` - Control script execution
- `CSP_FRAME_ANCESTORS = ("'none'",)` - Prevent iframe embedding
- `CSP_FORM_ACTION = ("'self'",)` - Restrict form submissions

**XSS Attack Prevention:**

- Input sanitization using `escape()` and `strip_tags()`
- Output encoding in templates
- Suspicious pattern detection in form inputs

### 5. Input Validation & Sanitization

**Form Security Measures:**

- Comprehensive field validation with length limits
- HTML tag stripping using `strip_tags()`
- XSS pattern detection (script tags, javascript:, etc.)
- Special character count validation
- Required field enforcement

**Example Validation:**

```python
def clean_title(self):
    title = strip_tags(escape(self.cleaned_data.get('title', '').strip()))

    # Check for suspicious patterns
    suspicious_patterns = [r'<script', r'javascript:', r'vbscript:']
    for pattern in suspicious_patterns:
        if re.search(pattern, title.lower()):
            raise ValidationError("Invalid characters detected.")

    return title
```

### 6. Secure Authentication & Authorization

**Permission System:**

- Custom permissions per model (can_view, can_create, can_edit, can_delete)
- `@permission_required` decorators with `raise_exception=True`
- Role-based access control (Admin, Librarian, Member)
- Group-based permission assignment

**Session Security:**

- Session timeout (1 hour)
- HTTPOnly session cookies
- Secure session cookies (HTTPS only)

### 7. Security Logging & Monitoring

**Comprehensive Logging:**

- Security event logging (login attempts, permission violations)
- Form validation failures
- Suspicious input detection
- File rotation with 15MB limit and 10 backups

**Log Configuration:**

```python
LOGGING = {
    'loggers': {
        'django.security': {
            'handlers': ['file', 'console'],
            'level': 'WARNING',
        },
    },
}
```

### 8. HTTP Security Headers

**Headers Implemented:**

- `Strict-Transport-Security` - Force HTTPS
- `X-Content-Type-Options: nosniff` - Prevent MIME sniffing
- `X-Frame-Options: DENY` - Prevent clickjacking
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Cross-Origin-Opener-Policy: same-origin`

## Template Security Implementation

### Secure Templates Created

**1. Book List Template (`bookshelf/templates/bookshelf/book_list.html`):**
- CSRF-protected search functionality
- Permission-based UI element display
- XSS-safe output rendering with proper escaping
- Security status indicators
- Responsive design with Bootstrap 5

**2. Form Example Template (`bookshelf/templates/bookshelf/form_example.html`):**
- Comprehensive CSRF protection demonstration
- Input validation error display
- Security feature indicators
- Client-side validation enhancements
- Educational security documentation

**Template Security Features:**
- `{% csrf_token %}` in all forms
- Proper HTML escaping for user content
- Permission-based conditional rendering
- CSP-compliant inline styles and scripts
- Secure form attributes (`autocomplete="off"`, `maxlength`, etc.)

## URL Configuration Security

**Updated URL Patterns:**

```python
# bookshelf/urls.py - All routes require appropriate permissions
urlpatterns = [
    path('', views.book_list, name='book_list'),                    # can_view_all_books
    path('book/<int:book_id>/', views.book_detail_view, name='book_detail'),  # can_view
    path('create/', views.create_book, name='create_book'),         # can_create
    path('edit/<int:book_id>/', views.edit_book, name='edit_book'), # can_edit
    path('delete/<int:book_id>/', views.delete_book, name='delete_book'),  # can_delete
    path('bulk/', views.bulk_operations, name='bulk_operations'),   # can_bulk_operations
    path('search/', views.search_books, name='search_books'),       # can_view_all_books
    path('form-example/', views.form_example, name='form_example'), # login_required
]
```

## Security Testing

### Manual Security Tests

1. **CSRF Protection:**
   - Remove `{% csrf_token %}` from forms → Should receive 403 Forbidden
   - Submit forms from external sites → Should be blocked

2. **XSS Prevention:**
   - Input `<script>alert('XSS')</script>` in forms → Should be sanitized
   - Check output encoding in templates → HTML should be escaped

3. **SQL Injection:**
   - Input `'; DROP TABLE books; --` in search → Should be safe
   - Special characters in form fields → Should be properly escaped

4. **Permission Testing:**
   - Access restricted URLs without permissions → Should receive 403
   - Test role-based access control → Each role should have appropriate access

5. **Template Security:**
   - Verify CSRF tokens are present in all forms
   - Test form validation error display
   - Check permission-based UI element visibility

### Test Users Available

```
Viewer User:     viewer_user / testpass123  (Read-only access)
Editor User:     editor_user / testpass123  (Create, Edit access)
Admin User:      admin_user / testpass123   (Full access)
```

## Production Deployment Checklist

### Critical Security Settings
- [ ] Set `DEBUG = False`
- [ ] Use environment variables for `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Enable HTTPS and SSL redirect
- [ ] Set all `*_SECURE` cookie settings to `True`

### Infrastructure Security
- [ ] Configure reverse proxy (nginx/Apache) for static files
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Enable security logging and monitoring
- [ ] Regular security updates and dependency scanning
- [ ] Configure CSP reporting endpoint
- [ ] Set up automated backups

### Template Security Verification
- [ ] Verify all templates include CSRF tokens
- [ ] Test form validation error handling
- [ ] Confirm permission-based UI rendering
- [ ] Validate XSS protection in user-generated content

## Installation & Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Database Setup

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Security Groups and Permissions

```bash
python manage.py setup_groups_permissions
```

### 4. Create Test Users

```bash
python manage.py test_permissions
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

## Usage Examples

### Accessing Secure Views

1. **Book List with Permissions:**
   - URL: `/bookshelf/`
   - Requires: `bookshelf.can_view_all_books` permission
   - Features: Search, pagination, permission-based actions

2. **Form Security Demo:**
   - URL: `/bookshelf/form-example/`
   - Requires: User authentication
   - Demonstrates: CSRF protection, input validation, XSS prevention

3. **Role-Based Access:**
   - Admin Dashboard: `/admin/` (Admin role + permissions)
   - Librarian View: `/librarian/` (Librarian role + library management)
   - Member View: `/member/` (Member role + basic view access)

## Security Dependencies

```txt
asgiref==3.9.1
Django==5.2.4
sqlparse==0.5.3
tzdata==2025.2
Pillow>=10.0.0
django-csp>=3.7  # Content Security Policy (optional)
```

## Key Security Files

- `LibraryProject/settings.py` - Security configuration
- `bookshelf/forms.py` - Secure form validation  
- `bookshelf/views.py` - Secure view implementation
- `bookshelf/templates/bookshelf/` - CSRF-protected templates
- `relationship_app/views.py` - Permission-protected views
- `relationship_app/management/commands/` - Security setup utilities

## Compliance Standards

This implementation follows:

- **OWASP Top 10** security guidelines
- **Django Security Best Practices** documentation
- **PCI DSS Level 1** requirements (where applicable)
- **GDPR** data protection principles
- **NIST Cybersecurity Framework** controls

## Security Monitoring

The application logs security events including:
- Failed authentication attempts
- Permission violations
- Suspicious input patterns
- Form validation failures
- CSRF token mismatches

Monitor `logs/security.log` for security events and configure alerting for production environments.

## Support & Contributing

For security issues or questions:
1. Review Django security documentation
2. Check OWASP guidelines for web application security
3. Test security features using provided test users
4. Report security vulnerabilities through appropriate channels

**Remember:** Security is an ongoing process. Regularly update dependencies, review logs, and test security measures.