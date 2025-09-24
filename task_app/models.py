from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, role=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        email = self.normalize_email(email)
        # Use strings directly for role defaults
        user = self.model(
            username=username,
            email=email,
            role=role if role else 'USER',  # default to USER
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Force role to SUPERADMIN directly as string
        return self.create_user(username, email, password, role='SUPERADMIN', **extra_fields)


class CustomUser(AbstractUser):
    ROLE_SUPERADMIN = 'SUPERADMIN'
    ROLE_ADMIN = 'ADMIN'
    ROLE_USER = 'USER'
    ROLE_CHOICES = [
        (ROLE_SUPERADMIN, 'SuperAdmin'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_USER, 'User')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_USER)
    assigned_admin = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_users')

    objects = CustomUserManager()  # Assign manager here

    def is_superadmin(self):
        return self.role == self.ROLE_SUPERADMIN
    
    def is_admin(self):
        return self.role == self.ROLE_ADMIN
    
    def is_user(self):
        return self.role == self.ROLE_USER
    

class Task(models.Model):
    STATUS_PENDING = 'Pending'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_COMPLETED = 'Completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='tasks')
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def mark_completed(self, report: str, hours):
        self.status = self.STATUS_COMPLETED
        self.completion_report = report
        self.worked_hours = hours
        self.save()

    def __str__(self):
        return f"{self.title} ({self.status})"
