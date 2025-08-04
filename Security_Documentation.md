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

### Test Users Available

```
Viewer User:     viewer_user / testpass123  (Read-only access)
Editor User:     editor_user / testpass123  (Create, Edit access)
Admin User:      admin_user / testpass123   (Full access)
```

## Production Deployment Checklist

- [ ] Set `DEBUG = False`
- [ ] Use environment variables for `SECRET_KEY`
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Enable HTTPS and SSL redirect
- [ ] Set all `*_SECURE` cookie settings to `True`
- [ ] Configure reverse proxy (nginx/Apache) for static files
- [ ] Set up proper database (PostgreSQL/MySQL)
- [ ] Enable security logging and monitoring
- [ ] Regular security updates and dependency scanning
- [ ] Configure CSP reporting endpoint
- [ ] Set up automated backups

## Usage

1. **Setup Security Groups:**

   ```bash
   python manage.py setup_groups_permissions
   ```

2. **Create Test Users:**

   ```bash
   python manage.py test_permissions
   ```

3. **Run Security Tests:**
   - Test form submissions with malicious input
   - Verify permission restrictions
   - Check HTTPS redirects in production

## Security Dependencies

```
Django>=5.2.4
django-csp>=3.7  # Content Security Policy
```

## Key Security Files

- `LibraryProject/settings.py` - Security configuration
- `bookshelf/forms.py` - Secure form validation
- `bookshelf/views.py` - Secure view implementation
- `relationship_app/views.py` - Permission-protected views
- Templates with CSRF tokens and secure practices

## Compliance

This implementation follows:

- OWASP Top 10 security guidelines
- Django security best practices
- PCI DSS Level 1 requirements (where applicable)
- GDPR data protection principles
