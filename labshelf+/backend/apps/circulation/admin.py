from django.contrib import admin

from .models import Fine, Loan, Reservation


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ('book', 'member', 'tenant', 'checkout_date', 'due_date', 'status', 'renewals')
    list_filter = ('tenant', 'status')
    search_fields = ('book__title', 'member__name')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'tenant', 'queue_position', 'status', 'expiry_date')
    list_filter = ('tenant', 'status')


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = ('loan', 'tenant', 'amount', 'status', 'created_at')
    list_filter = ('tenant', 'status')

# Register your models here.
