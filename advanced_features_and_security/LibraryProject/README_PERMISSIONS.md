# Django LibraryProject - Permissions and Groups System

**Directory**: `LibraryProject/README_PERMISSIONS.md`

## 📋 Overview

This Django LibraryProject implements a comprehensive **permissions and groups system** to control access to various parts of the application. The system enhances security and functionality by restricting actions based on user roles and assigned permissions.

## 🏗️ System Architecture

### Custom Permissions Defined

The system uses **custom permissions** defined in model Meta classes to control specific actions:

```python
# bookshelf/models.py & relationship_app/models.py
class Book(models.Model):
    # ... model fields ...

    class Meta:
        permissions = [
            ("can_view", "Can view book"),
            ("can_create", "Can create book"),
            ("can_edit", "Can edit book"),
            ("can_delete", "Can delete book"),
            ("can_view_all_books", "Can view all books"),
            ("can_manage_authors", "Can manage book authors"),
            ("can_bulk_operations", "Can perform bulk operations"),
        ]
```

## 👥 Groups Configuration

### Three Main User Groups

#### 1. **Viewers Group**

- **Purpose**: Read-only access to library content
- **Permissions**:
  - `can_view` - View individual book details
  - `can_view_all_books` - Access book lists
- **Typical Users**: General library visitors, students

#### 2. **Editors Group**

- **Purpose**: Content management and curation
- **Permissions**:
  - All Viewer permissions +
  - `can_create` - Add new books
  - `can_edit` - Modify existing books
  - `can_manage_authors` - Manage book authors
  - `can_manage_library` - Library management
- **Typical Users**: Library staff, content managers

#### 3. **Admins Group**

- **Purpose**: Full system administration
- **Permissions**:
  - All Editor permissions +
  - `can_delete` - Remove books
  - `can_bulk_operations` - Bulk edit/delete operations
  - `can_view_library_stats` - View system statistics
- **Typical Users**: System administrators, head librarians

## 🔐 Permission Enforcement in Views

### Decorator-Based Protection

Views are protected using Django's `@permission_required` decorator with `raise_exception=True`:

```python
# Example from bookshelf/views.py
@permission_required('bookshelf.can_view_all_books', raise_exception=True)
def book_list(request):
    """Requires can_view_all_books permission to access"""
    books = Book.objects.all()
    return render(request, 'bookshelf/book_list.html', {'books': books})

@permission_required('bookshelf.can_create', raise_exception=True)
@login_required
def create_book(request):
    """Requires can_create permission - typically Editors and Admins"""
    # ... book creation logic ...
```

### Permission Mapping

| Action          | Required Permission              | Allowed Groups           | Views Protected                |
| --------------- | -------------------------------- | ------------------------ | ------------------------------ |
| View Books      | `can_view`, `can_view_all_books` | Viewers, Editors, Admins | `book_list()`, `book_detail()` |
| Create Books    | `can_create`                     | Editors, Admins          | `add_book()`, `create_book()`  |
| Edit Books      | `can_edit`                       | Editors, Admins          | `edit_book()`                  |
| Delete Books    | `can_delete`                     | Admins Only              | `delete_book()`                |
| Bulk Operations | `can_bulk_operations`            | Admins Only              | `bulk_operations()`            |

## ⚙️ Setup and Configuration

### 1. Initial Setup

```bash
# Apply database migrations
python manage.py makemigrations
python manage.py migrate
```

### 2. Automated Groups and Permissions Setup

```bash
# Run the setup command to create groups and assign permissions
python manage.py setup_groups_permissions
```

**What this command does**:

- Creates Viewers, Editors, and Admins groups
- Assigns appropriate permissions to each group
- Provides setup confirmation and summary

### 3. Create Test Users (Optional)

```bash
# Create test users for testing permissions
python manage.py test_permissions
```

**Generated test accounts**:

- **viewer_user** / testpass123 (Viewers group)
- **editor_user** / testpass123 (Editors group)
- **admin_user** / testpass123 (Admins group)

## 🧪 Testing the Permission System

### Manual Testing Steps

1. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

2. **Test URLs with different user roles**:

   - `http://127.0.0.1:8000/books/` - Book list (requires can_view_all_books)
   - `http://127.0.0.1:8000/add_book/` - Add book (requires can_create)
   - `http://127.0.0.1:8000/bookshelf/` - Bookshelf app (permission-protected)
   - `http://127.0.0.1:8000/admin/` - Admin interface

3. **Expected Behavior**:
   - **viewer_user**: Can view books, blocked from create/edit/delete
   - **editor_user**: Can view, create, and edit books, blocked from delete
   - **admin_user**: Full access to all operations

### Testing Access Control

| User Type | Can View | Can Create | Can Edit | Can Delete | Can Bulk Ops |
| --------- | -------- | ---------- | -------- | ---------- | ------------ |
| Viewer    | ✅       | ❌         | ❌       | ❌         | ❌           |
| Editor    | ✅       | ✅         | ✅       | ❌         | ❌           |
| Admin     | ✅       | ✅         | ✅       | ✅         | ✅           |

## 🔧 Managing Users and Groups

### Via Django Admin

1. Access admin at `http://127.0.0.1:8000/admin/`
2. Navigate to **Authentication and Authorization** → **Groups**
3. Select a group to view/modify permissions
4. Navigate to **Users** to assign users to groups

### Programmatically

```python
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

# Create user and assign to group
user = User.objects.create_user(username='newuser', email='user@example.com')
editors_group = Group.objects.get(name='Editors')
user.groups.add(editors_group)
```

## 🚦 Error Handling

### Permission Denied (403 Forbidden)

When users lack required permissions, the system shows a 403 Forbidden page due to `raise_exception=True` in decorators.

### Handling in Templates

Templates can check permissions dynamically:

```html
{% if user.has_perm:'bookshelf.can_create' %}
<a href="{% url 'bookshelf:create_book' %}">Add New Book</a>
{% endif %} {% if user.has_perm:'bookshelf.can_delete' %}
<button class="btn btn-danger">Delete</button>
{% endif %}
```

## 📁 File Structure

### Key Files for Permissions System

```
LibraryProject/
├── bookshelf/
│   ├── models.py              # Custom permissions defined
│   ├── views.py               # Permission-protected views
│   └── urls.py                # Protected URL patterns
├── relationship_app/
│   ├── models.py              # Enhanced permissions + UserProfile
│   ├── views.py               # Role-based + permission views
│   └── management/commands/
│       ├── setup_groups_permissions.py  # Automated setup
│       └── test_permissions.py          # Test user creation
└── README_PERMISSIONS.md      # This documentation
```

## 🔄 Maintenance and Updates

### Adding New Permissions

1. Add permission to model's Meta class
2. Create and run migration: `python manage.py makemigrations && python manage.py migrate`
3. Update groups: `python manage.py setup_groups_permissions`
4. Update views with `@permission_required` decorators

### Modifying Group Permissions

1. Edit `setup_groups_permissions.py` command
2. Re-run: `python manage.py setup_groups_permissions`
3. Existing group permissions will be updated

## 🛡️ Security Best Practices

1. **Always use `raise_exception=True`** in permission decorators
2. **Combine with `@login_required`** for authenticated views
3. **Check permissions in templates** before showing UI elements
4. **Use groups instead of individual permission assignment** for scalability
5. **Regular permission audits** through Django admin interface

## 📞 Troubleshooting

### Common Issues

**Issue**: Permission not found error

```
Permission matching query does not exist
```

**Solution**: Run migrations and setup command:

```bash
python manage.py migrate
python manage.py setup_groups_permissions
```

**Issue**: User can't access protected views
**Solution**: Check user group assignment in Django admin

**Issue**: Templates not showing permission-based elements  
**Solution**: Ensure user has required permissions and check template syntax

## 📚 Related Django Documentation

- [Django Permissions and Authorization](https://docs.djangoproject.com/en/stable/topics/auth/default/#permissions-and-authorization)
- [Django Groups](https://docs.djangoproject.com/en/stable/topics/auth/default/#groups)
- [Permission Decorators](https://docs.djangoproject.com/en/stable/topics/auth/default/#the-permission-required-decorator)

---

**Last Updated**: August 2025  
**Django Version**: 5.2.4  
**Project**: LibraryProject Advanced Features and Security
