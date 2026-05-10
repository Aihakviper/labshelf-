from datetime import timedelta

from django import forms

from backend.apps.catalog.models import Book
from backend.apps.circulation.models import Loan, Reservation
from backend.apps.tenants.models import LibraryUser, Tenant


class TenantScopedFormMixin:
    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.tenant = tenant

    def _post_clean(self):
        if self.tenant and hasattr(self.instance, 'tenant_id'):
            self.instance.tenant = self.tenant
        super()._post_clean()


class BookForm(TenantScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'category', 'shelf_location', 'total_copies']

    def save(self, commit=True):
        book = super().save(commit=False)
        book.tenant = self.tenant
        if commit:
            book.save()
        return book


class LoanForm(TenantScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Loan
        fields = ['book', 'member', 'checked_out_by']

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(tenant=tenant)
        self.fields['member'].queryset = LibraryUser.objects.filter(tenant=tenant, role=LibraryUser.MEMBER)
        self.fields['checked_out_by'].queryset = LibraryUser.objects.filter(
            tenant=tenant,
            role__in=[LibraryUser.ADMIN, LibraryUser.LIBRARIAN],
        )

    def save(self, commit=True):
        loan = super().save(commit=False)
        loan.tenant = self.tenant
        loan.due_date = loan.checkout_date + timedelta(days=self.tenant.borrowing_days)
        if commit:
            loan.full_clean()
            loan.save()
        return loan


class ReservationForm(TenantScopedFormMixin, forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['book', 'user']

    def __init__(self, *args, tenant=None, **kwargs):
        super().__init__(*args, tenant=tenant, **kwargs)
        self.fields['book'].queryset = Book.objects.filter(tenant=tenant)
        self.fields['user'].queryset = LibraryUser.objects.filter(tenant=tenant, role=LibraryUser.MEMBER)

    def save(self, commit=True):
        reservation = super().save(commit=False)
        reservation.tenant = self.tenant
        reservation.queue_position = Reservation.next_position(reservation.book)
        if commit:
            reservation.full_clean()
            reservation.save()
        return reservation


class MemberForm(TenantScopedFormMixin, forms.ModelForm):
    class Meta:
        model = LibraryUser
        fields = ['name', 'email', 'student_id']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if LibraryUser.objects.filter(tenant=self.tenant, email=email).exists():
            raise forms.ValidationError('A member with this email already exists.')
        return email

    def save(self, commit=True):
        member = super().save(commit=False)
        member.tenant = self.tenant
        member.role = LibraryUser.MEMBER
        if commit:
            member.save()
        return member


class TenantSwitchForm(forms.Form):
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all())
