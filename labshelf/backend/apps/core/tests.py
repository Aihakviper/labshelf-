import json

from django.test import TestCase

from backend.apps.catalog.models import Book
from backend.apps.circulation.models import Loan, Reservation
from backend.apps.tenants.models import LibraryUser, Tenant


class CirculationApiTests(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Demo School', slug='demo')
        self.librarian = LibraryUser.objects.create(
            tenant=self.tenant,
            name='Librarian',
            email='librarian@example.com',
            role=LibraryUser.LIBRARIAN,
        )
        self.member = LibraryUser.objects.create(
            tenant=self.tenant,
            name='Member',
            email='member@example.com',
            role=LibraryUser.MEMBER,
        )
        self.book = Book.objects.create(
            tenant=self.tenant,
            title='Demo Book',
            author='Demo Author',
            total_copies=2,
        )

    def test_checkout_sets_tenant_before_model_validation(self):
        self.client.get('/api/dashboard/')

        response = self.client.post(
            '/api/loans/',
            data=json.dumps({
                'book': self.book.id,
                'member': self.member.id,
                'checked_out_by': self.librarian.id,
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Loan.objects.filter(tenant=self.tenant, book=self.book, member=self.member).exists())

    def test_reservation_sets_tenant_before_model_validation(self):
        self.client.get('/api/dashboard/')

        response = self.client.post(
            '/api/reservations/',
            data=json.dumps({
                'book': self.book.id,
                'user': self.member.id,
            }),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Reservation.objects.filter(tenant=self.tenant, book=self.book, user=self.member).exists())
