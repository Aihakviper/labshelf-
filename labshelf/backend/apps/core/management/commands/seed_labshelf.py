from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from backend.apps.catalog.models import Book
from backend.apps.circulation.models import Fine, Loan, Reservation
from backend.apps.tenants.models import LibraryUser, Tenant


class Command(BaseCommand):
    help = 'Load LabShelf+ demo data for Nigerian schools and institutions.'

    def handle(self, *args, **options):
        tenant, _ = Tenant.objects.update_or_create(
            slug='greenfield',
            defaults={
                'name': 'Greenfield Model Secondary School',
                'subscription_plan': Tenant.GROWTH,
                'borrowing_days': 5,
                'max_renewals': 2,
                'reservation_limit': 10,
                'fine_per_day': 50,
            },
        )
        campus, _ = Tenant.objects.update_or_create(
            slug='lagos-open-learning',
            defaults={
                'name': 'Lagos Open Learning Centre',
                'subscription_plan': Tenant.BASIC,
                'borrowing_days': 5,
                'max_renewals': 2,
                'reservation_limit': 10,
                'fine_per_day': 75,
            },
        )

        librarian, _ = LibraryUser.objects.update_or_create(
            tenant=tenant,
            email='librarian@greenfield.edu.ng',
            defaults={'name': 'Amina Yusuf', 'role': LibraryUser.LIBRARIAN},
        )
        members = []
        for name, email, student_id in [
            ('Chidera Okafor', 'chidera@greenfield.edu.ng', 'GMS/24/031'),
            ('Sodiq Balogun', 'sodiq@greenfield.edu.ng', 'GMS/24/044'),
            ('Maryam Danladi', 'maryam@greenfield.edu.ng', 'GMS/24/058'),
        ]:
            member, _ = LibraryUser.objects.update_or_create(
                tenant=tenant,
                email=email,
                defaults={'name': name, 'role': LibraryUser.MEMBER, 'student_id': student_id},
            )
            members.append(member)

        LibraryUser.objects.update_or_create(
            tenant=campus,
            email='admin@lolc.ng',
            defaults={'name': 'Tunde Adeyemi', 'role': LibraryUser.ADMIN},
        )

        books = []
        for item in [
            ('New General Mathematics 2', 'M. F. Macrae', '9789781291011', 'Mathematics', 'MATH-A2', 4),
            ('Things Fall Apart', 'Chinua Achebe', '9780385474542', 'Literature', 'LIT-C1', 3),
            ('Essential Biology for Senior Secondary Schools', 'M. C. Michael', '9789781753199', 'Science', 'SCI-B4', 2),
            ('The Joys of Motherhood', 'Buchi Emecheta', '9780435909727', 'Literature', 'LIT-C3', 1),
            ('Government for Senior Secondary Schools', 'B. O. Nwankwo', '9789782789029', 'Civic Studies', 'GOV-A1', 2),
        ]:
            book, _ = Book.objects.update_or_create(
                tenant=tenant,
                isbn=item[2],
                defaults={
                    'title': item[0],
                    'author': item[1],
                    'category': item[3],
                    'shelf_location': item[4],
                    'total_copies': item[5],
                },
            )
            books.append(book)

        old_due = timezone.localdate() - timedelta(days=3)
        active_due = timezone.localdate() + timedelta(days=4)
        overdue, _ = Loan.objects.get_or_create(
            tenant=tenant,
            book=books[3],
            member=members[0],
            defaults={
                'checked_out_by': librarian,
                'checkout_date': old_due - timedelta(days=5),
                'due_date': old_due,
                'status': Loan.OVERDUE,
            },
        )
        Fine.objects.get_or_create(
            tenant=tenant,
            loan=overdue,
            defaults={'amount': overdue.days_overdue * tenant.fine_per_day, 'status': Fine.UNPAID},
        )
        Loan.objects.get_or_create(
            tenant=tenant,
            book=books[1],
            member=members[1],
            defaults={
                'checked_out_by': librarian,
                'checkout_date': timezone.localdate(),
                'due_date': active_due,
                'status': Loan.ACTIVE,
            },
        )
        Reservation.objects.get_or_create(
            tenant=tenant,
            book=books[3],
            user=members[2],
            defaults={'queue_position': 1, 'status': Reservation.WAITING},
        )

        self.stdout.write(self.style.SUCCESS('LabShelf+ demo data loaded.'))
