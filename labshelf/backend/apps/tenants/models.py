from django.db import models


class Tenant(models.Model):
    BASIC = 'basic'
    GROWTH = 'growth'
    ENTERPRISE = 'enterprise'
    PLAN_CHOICES = [
        (BASIC, 'Basic'),
        (GROWTH, 'Growth'),
        (ENTERPRISE, 'Enterprise'),
    ]

    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    subscription_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=GROWTH)
    borrowing_days = models.PositiveSmallIntegerField(default=5)
    max_renewals = models.PositiveSmallIntegerField(default=2)
    reservation_limit = models.PositiveSmallIntegerField(default=10)
    fine_per_day = models.DecimalField(max_digits=8, decimal_places=2, default=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class LibraryUser(models.Model):
    ADMIN = 'admin'
    LIBRARIAN = 'librarian'
    MEMBER = 'member'
    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (LIBRARIAN, 'Librarian'),
        (MEMBER, 'Member'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
    name = models.CharField(max_length=160)
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    student_id = models.CharField(max_length=60, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = [('tenant', 'email')]

    def __str__(self):
        return f'{self.name} ({self.get_role_display()})'

# Create your models here.
