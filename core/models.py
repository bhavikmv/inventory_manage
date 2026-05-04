from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from datetime import date

class CustomUserManager(UserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Auto-generate a username from email if not provided
        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Base user model for both Admins and Students, using email for login."""
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"


class Student(models.Model):
    """Student-specific data, linked to the User model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    phone = models.CharField(max_length=15, blank=True)
    gr_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.gr_number})"


class Booking(models.Model):
    """Represents a gadget booking/request by a student."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    ]

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    gadget = models.ForeignKey('gadgets.Gadget', on_delete=models.CASCADE, related_name='bookings')
    
    start_date = models.DateField()
    end_date = models.DateField()
    days = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField(default=1)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    
    # Admin notes
    admin_notes = models.TextField(blank=True)
    
    # Approval details
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_bookings')
    
    # Timestamps
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.gadget.name} ({self.status})"

    @property
    def is_overdue(self):
        """Check if approved booking is past end date and not returned."""
        if self.status == 'approved' and self.end_date < date.today():
            return True
        return False

    def mark_returned(self):
        self.status = 'returned'
        self.returned_at = timezone.now()
        self.save()
