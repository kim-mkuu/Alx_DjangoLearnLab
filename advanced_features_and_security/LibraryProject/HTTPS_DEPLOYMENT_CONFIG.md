# HTTPS Deployment Configuration Guide

## Step 4: Deployment Configuration for HTTPS Support

This document provides comprehensive instructions for configuring your deployment environment to support HTTPS with SSL/TLS certificates.

---

## 1. Nginx Configuration (Recommended)

### Complete Nginx Configuration (`/etc/nginx/sites-available/libraryproject`)

```nginx
# LibraryProject HTTPS Configuration
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Security: Return 301 redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS Server Configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Certificate Configuration
    ssl_certificate /etc/ssl/certs/yourdomain.com.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.com.key;
    
    # Modern SSL Configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # SSL Security Settings
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers (Additional to Django settings)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Django Application Proxy Settings
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Security: Hide server information
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files serving
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files serving (with security restrictions)
    location /media/ {
        alias /path/to/your/project/media/;
        expires 1M;
        add_header Cache-Control "public";
        
        # Security: Prevent execution of scripts in media directory
        location ~* \.(php|py|js|pl|sh|cgi)$ {
            deny all;
        }
    }
    
    # Security: Block access to sensitive files
    location ~ /\.(ht|git|env) {
        deny all;
    }
    
    # Performance: Gzip compression
    gzip on;
    gzip_vary on;
    gzip_types text/plain text/css application/json application/javascript text/javascript;
}
```

### Enable the Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/libraryproject /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

---

## 2. Let's Encrypt SSL Certificate Setup

### Install Certbot

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### Obtain SSL Certificate

```bash
# Automatic nginx configuration
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Manual certificate only (if you prefer manual nginx config)
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

### Setup Automatic Renewal

```bash
# Test automatic renewal
sudo certbot renew --dry-run

# Add to crontab for automatic renewal
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 3. Apache Configuration (Alternative)

### Apache HTTPS Configuration (`/etc/apache2/sites-available/libraryproject-ssl.conf`)

```apache
# HTTP to HTTPS Redirect
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # Security: Redirect to HTTPS
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

# HTTPS Configuration
<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/ssl/certs/yourdomain.com.crt
    SSLCertificateKeyFile /etc/ssl/private/yourdomain.com.key
    SSLCertificateChainFile /etc/ssl/certs/intermediate.crt
    
    # Modern SSL Configuration
    SSLProtocol -all +TLSv1.2 +TLSv1.3
    SSLCipherSuite ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!SHA1:!DSS
    SSLHonorCipherOrder off
    
    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    Header always set X-Content-Type-Options nosniff
    Header always set X-Frame-Options DENY
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    
    # Django Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
    
    # Set headers for Django
    ProxyPassReverse / http://127.0.0.1:8000/
    ProxyPassReverseMatch ^/(.*) http://127.0.0.1:8000/$1
    
    # Static files
    Alias /static/ /path/to/your/project/staticfiles/
    <Directory "/path/to/your/project/staticfiles/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 year"
    </Directory>
    
    # Media files
    Alias /media/ /path/to/your/project/media/
    <Directory "/path/to/your/project/media/">
        Require all granted
        ExpiresActive On
        ExpiresDefault "access plus 1 month"
        
        # Security: Block script execution
        <FilesMatch "\.(php|py|js|pl|sh|cgi)$">
            Require all denied
        </FilesMatch>
    </Directory>
</VirtualHost>
```

---

## 4. Django Environment Configuration

### Production Environment Variables (`.env` file)

```bash
# Production Environment Configuration
DJANGO_ENV=production
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-super-secret-production-key-here
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Configuration (use PostgreSQL in production)
DATABASE_URL=postgresql://username:password@localhost:5432/libraryproject

# Security Settings
DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

### Updated settings.py for Environment Variables

Add to your settings.py:

```python
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Use environment variables for security settings
SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
SESSION_COOKIE_SECURE = os.environ.get('DJANGO_SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('DJANGO_CSRF_COOKIE_SECURE', 'False').lower() == 'true'

# Proxy configuration for reverse proxies
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

---

## 5. Deployment Scripts

### HTTPS Deployment Script (`deploy_https.sh`)

```bash
#!/bin/bash
# HTTPS Deployment Script for LibraryProject

set -e  # Exit on any error

echo "🚀 Starting HTTPS deployment for LibraryProject..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing nginx and certbot..."
sudo apt install nginx certbot python3-certbot-nginx -y

# Copy nginx configuration
echo "⚙️ Configuring nginx..."
sudo cp nginx/libraryproject.conf /etc/nginx/sites-available/libraryproject
sudo ln -sf /etc/nginx/sites-available/libraryproject /etc/nginx/sites-enabled/

# Test nginx configuration
echo "🔍 Testing nginx configuration..."
sudo nginx -t

# Install SSL certificate
echo "🔐 Installing SSL certificate..."
sudo certbot --nginx -d $DOMAIN_NAME --non-interactive --agree-tos --email $EMAIL

# Setup auto-renewal
echo "🔄 Setting up SSL certificate auto-renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart nginx

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run Django checks
echo "🔍 Running Django security checks..."
python manage.py check --deploy

echo "✅ HTTPS deployment completed successfully!"
echo "🌐 Your site should now be available at: https://$DOMAIN_NAME"
```

### Make script executable and run:

```bash
chmod +x deploy_https.sh
export DOMAIN_NAME=yourdomain.com
export EMAIL=your@email.com
./deploy_https.sh
```

---

## 6. Testing Your HTTPS Configuration

### Manual Testing Commands

```bash
# Test HTTP to HTTPS redirect
curl -I http://yourdomain.com

# Test HTTPS response
curl -I https://yourdomain.com

# Test SSL certificate
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Test security headers
curl -I https://yourdomain.com | grep -E "(Strict-Transport-Security|X-Content-Type-Options|X-Frame-Options)"
```

### Online Testing Tools

1. **SSL Labs SSL Test**: https://www.ssllabs.com/ssltest/
   - Tests SSL certificate configuration
   - Provides security rating (aim for A+)

2. **Security Headers**: https://securityheaders.com/
   - Tests HTTP security headers
   - Provides recommendations

3. **HSTS Preload**: https://hstspreload.org/
   - Check HSTS preload eligibility
   - Submit for browser preload lists

---

## 7. Troubleshooting Common Issues

### Issue: Mixed Content Warnings

```html
<!-- In templates, ensure all resources use HTTPS or protocol-relative URLs -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
<!-- Or protocol-relative: -->
<link href="//cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
```

### Issue: Reverse Proxy Headers Not Working

Add to Django settings.py:

```python
# If using reverse proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
```

### Issue: Static Files Not Loading Over HTTPS

```python
# In settings.py, ensure static files URL is protocol-relative
STATIC_URL = '/static/'
# Or force HTTPS in production
if not DEBUG:
    STATIC_URL = 'https://yourdomain.com/static/'
```

---

## 8. Monitoring and Maintenance

### SSL Certificate Monitoring

```bash
# Check certificate expiry
echo | openssl s_client -servername yourdomain.com -connect yourdomain.com:443 2>/dev/null | openssl x509 -noout -dates

# Monitor certificate with script
#!/bin/bash
DOMAIN="yourdomain.com"
EXPIRY=$(echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
NOW_EPOCH=$(date +%s)
DAYS_LEFT=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

if [ $DAYS_LEFT -lt 30 ]; then
    echo "⚠️ SSL certificate expires in $DAYS_LEFT days!"
fi
```

### Security Monitoring

```bash
# Monitor security logs
tail -f /path/to/your/project/logs/security.log

# Check for security issues in Django
python manage.py check --deploy
```

This comprehensive deployment configuration ensures your Django application is properly configured for HTTPS with all necessary security measures in place.