from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from backend.apps.catalog.models import Book
from backend.apps.tenants.models import LibraryUser, Tenant

from .models import Fine, Loan, Reservation


class CirculationRuleTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(
            name='Rule Test School',
            slug='rule-test',
            borrowing_days=5,
            max_renewals=2,
            fine_per_day=50,
        )
        self.librarian = LibraryUser.objects.create(
            tenant=self.tenant,
            name='Librarian',
            email='librarian@test.ng',
            role=LibraryUser.LIBRARIAN,
        )
        self.member = LibraryUser.objects.create(
            tenant=self.tenant,
            name='Member',
            email='member@test.ng',
            role=LibraryUser.MEMBER,
        )
        self.book = Book.objects.create(
            tenant=self.tenant,
            title='Single Copy Book',
            author='Author',
            total_copies=1,
        )

    def test_checkout_consumes_available_copy(self):
        Loan.objects.create(
            tenant=self.tenant,
            book=self.book,
            member=self.member,
            checked_out_by=self.librarian,
            due_date=timezone.localdate() + timedelta(days=5),
        )

        self.assertEqual(self.book.available_copies, 0)

    def test_overdue_return_creates_fine_and_advances_reservation(self):
        loan = Loan.objects.create(
            tenant=self.tenant,
            book=self.book,
            member=self.member,
            checked_out_by=self.librarian,
            checkout_date=timezone.localdate() - timedelta(days=8),
            due_date=timezone.localdate() - timedelta(days=3),
            status=Loan.OVERDUE,
        )
        next_member = LibraryUser.objects.create(
            tenant=self.tenant,
            name='Next Member',
            email='next@test.ng',
            role=LibraryUser.MEMBER,
        )
        reservation = Reservation.objects.create(
            tenant=self.tenant,
            book=self.book,
            user=next_member,
            queue_position=1,
        )

        loan.mark_returned()
        reservation.refresh_from_db()

        self.assertEqual(Fine.objects.get(loan=loan).amount, 150)
        self.assertEqual(reservation.status, Reservation.READY)

    def test_renewal_limit_is_enforced(self):
        loan = Loan.objects.create(
            tenant=self.tenant,
            book=self.book,
            member=self.member,
            checked_out_by=self.librarian,
            due_date=timezone.localdate() + timedelta(days=5),
            renewals=2,
        )

        with self.assertRaises(ValidationError):
            loan.renew()

# Create your tests here.
