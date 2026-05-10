from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from backend.apps.catalog.models import Book
from backend.apps.tenants.models import LibraryUser, Tenant


class Loan(models.Model):
    ACTIVE = 'active'
    RETURNED = 'returned'
    OVERDUE = 'overdue'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (RETURNED, 'Returned'),
        (OVERDUE, 'Overdue'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='loans')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    member = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='loans')
    checked_out_by = models.ForeignKey(
        LibraryUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_loans',
    )
    checkout_date = models.DateField(default=timezone.localdate)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    renewals = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-checkout_date']

    def clean(self):
        if self.member.role != LibraryUser.MEMBER:
            raise ValidationError('Only member accounts can borrow books.')
        if self.book.tenant_id != self.tenant_id or self.member.tenant_id != self.tenant_id:
            raise ValidationError('Loan book and member must belong to the same tenant.')
        if not self.pk and self.book.available_copies <= 0:
            raise ValidationError('This book has no available copies.')

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.checkout_date + timedelta(days=self.tenant.borrowing_days)
        if self.status != self.RETURNED and self.due_date < timezone.localdate():
            self.status = self.OVERDUE
        super().save(*args, **kwargs)

    @property
    def days_overdue(self):
        if self.status == self.RETURNED and self.return_date:
            comparison_date = self.return_date
        else:
            comparison_date = timezone.localdate()
        return max((comparison_date - self.due_date).days, 0)

    def mark_returned(self):
        self.return_date = timezone.localdate()
        self.status = self.RETURNED
        self.save()
        amount = self.days_overdue * self.tenant.fine_per_day
        if amount:
            Fine.objects.get_or_create(
                tenant=self.tenant,
                loan=self,
                defaults={'amount': amount, 'status': Fine.UNPAID},
            )
        Reservation.advance_queue(self.book)

    def renew(self):
        if self.renewals >= self.tenant.max_renewals:
            raise ValidationError('Maximum renewals reached.')
        self.renewals += 1
        self.due_date = self.due_date + timedelta(days=self.tenant.borrowing_days)
        self.save()

    def __str__(self):
        return f'{self.book} to {self.member}'


class Reservation(models.Model):
    WAITING = 'waiting'
    READY = 'ready'
    EXPIRED = 'expired'
    FULFILLED = 'fulfilled'
    CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (WAITING, 'Waiting'),
        (READY, 'Ready for pickup'),
        (EXPIRED, 'Expired'),
        (FULFILLED, 'Fulfilled'),
        (CANCELLED, 'Cancelled'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(LibraryUser, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    queue_position = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=WAITING)
    expiry_date = models.DateField(null=True, blank=True)
    notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['book', 'queue_position']

    def clean(self):
        if self.user.role != LibraryUser.MEMBER:
            raise ValidationError('Only members can reserve books.')
        if self.book.tenant_id != self.tenant_id or self.user.tenant_id != self.tenant_id:
            raise ValidationError('Reservation book and user must belong to the same tenant.')
        waiting_count = Reservation.objects.filter(
            tenant=self.tenant,
            book=self.book,
            status__in=[self.WAITING, self.READY],
        ).exclude(pk=self.pk).count()
        if waiting_count >= self.tenant.reservation_limit:
            raise ValidationError('Reservation queue is full for this book.')

    def save(self, *args, **kwargs):
        if not self.queue_position:
            self.queue_position = self.next_position(self.book)
        super().save(*args, **kwargs)

    @classmethod
    def next_position(cls, book):
        last = cls.objects.filter(book=book, status__in=[cls.WAITING, cls.READY]).order_by('-queue_position').first()
        return (last.queue_position + 1) if last else 1

    @classmethod
    def advance_queue(cls, book):
        ready = cls.objects.filter(book=book, status=cls.READY).exists()
        if ready or book.available_copies <= 0:
            return None
        next_reservation = cls.objects.filter(book=book, status=cls.WAITING).order_by('queue_position').first()
        if next_reservation:
            next_reservation.status = cls.READY
            next_reservation.notified_at = timezone.now()
            next_reservation.expiry_date = timezone.localdate() + timedelta(days=2)
            next_reservation.save()
        return next_reservation

    def __str__(self):
        return f'{self.book} reserved by {self.user}'


class Fine(models.Model):
    UNPAID = 'unpaid'
    PAID = 'paid'
    WAIVED = 'waived'
    STATUS_CHOICES = [
        (UNPAID, 'Unpaid'),
        (PAID, 'Paid'),
        (WAIVED, 'Waived'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='fines')
    loan = models.OneToOneField(Loan, on_delete=models.CASCADE, related_name='fine')
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=UNPAID)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['status', '-created_at']

    def __str__(self):
        return f'{self.amount} for {self.loan}'

# Create your models here.
