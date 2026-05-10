from django.db import models
from django.db.models import Count, Q

from backend.apps.tenants.models import Tenant


class Book(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=220)
    author = models.CharField(max_length=160)
    isbn = models.CharField(max_length=32, blank=True)
    category = models.CharField(max_length=100, default='General')
    shelf_location = models.CharField(max_length=60, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def active_loans_count(self):
        return self.loans.filter(status__in=['active', 'overdue']).count()

    @property
    def available_copies(self):
        return max(self.total_copies - self.active_loans_count, 0)

    @property
    def queue_size(self):
        return self.reservations.filter(status='waiting').count()

# Create your models here.
