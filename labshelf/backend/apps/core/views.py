import json

from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from backend.apps.catalog.models import Book
from backend.apps.circulation.models import Fine, Loan, Reservation
from backend.apps.tenants.models import LibraryUser, Tenant

from .forms import BookForm, LoanForm, MemberForm, ReservationForm


def current_tenant(request):
    tenant_id = request.session.get('tenant_id')
    tenant = Tenant.objects.filter(id=tenant_id).first()
    if tenant:
        return tenant
    tenant = Tenant.objects.order_by('name').first()
    if tenant:
        request.session['tenant_id'] = tenant.id
    return tenant


@ensure_csrf_cookie
def app_shell(request):
    return JsonResponse({
        'service': 'LabShelf+ API',
        'frontend': 'Run the Vite app from the frontend directory.',
    })


@ensure_csrf_cookie
def api_dashboard(request):
    tenant = current_tenant(request)
    if tenant is None:
        return JsonResponse({'seeded': False})

    return JsonResponse({'seeded': True, 'data': dashboard_payload(tenant)})


@require_http_methods(['POST'])
def api_switch_tenant(request):
    payload = parse_json(request)
    tenant = get_object_or_404(Tenant, id=payload.get('tenant_id'))
    request.session['tenant_id'] = tenant.id
    return JsonResponse({'data': dashboard_payload(tenant)})


@require_http_methods(['POST'])
def api_create_book(request):
    tenant = current_tenant(request)
    form = BookForm(parse_json(request), tenant=tenant)
    if form.is_valid():
        form.save()
        return JsonResponse({'message': 'Book added to the catalog.', 'data': dashboard_payload(tenant)})
    return JsonResponse({'error': first_error(form)}, status=400)


@require_http_methods(['POST'])
def api_checkout_book(request):
    tenant = current_tenant(request)
    form = LoanForm(parse_json(request), tenant=tenant)
    if form.is_valid():
        try:
            form.save()
            return JsonResponse({'message': 'Loan created and due date assigned.', 'data': dashboard_payload(tenant)})
        except ValidationError as exc:
            return JsonResponse({'error': '; '.join(exc.messages)}, status=400)
    return JsonResponse({'error': first_error(form)}, status=400)


@require_http_methods(['POST'])
def api_reserve_book(request):
    tenant = current_tenant(request)
    form = ReservationForm(parse_json(request), tenant=tenant)
    if form.is_valid():
        try:
            form.save()
            return JsonResponse({'message': 'Reservation added to the queue.', 'data': dashboard_payload(tenant)})
        except ValidationError as exc:
            return JsonResponse({'error': '; '.join(exc.messages)}, status=400)
    return JsonResponse({'error': first_error(form)}, status=400)


@require_http_methods(['POST'])
def api_create_member(request):
    tenant = current_tenant(request)
    form = MemberForm(parse_json(request), tenant=tenant)
    if form.is_valid():
        form.save()
        return JsonResponse({'message': 'Member added.', 'data': dashboard_payload(tenant)})
    return JsonResponse({'error': first_error(form)}, status=400)


@require_http_methods(['POST'])
def api_return_loan(request, loan_id):
    tenant = current_tenant(request)
    loan = get_object_or_404(Loan, id=loan_id, tenant=tenant)
    loan.mark_returned()
    return JsonResponse({'message': 'Book returned. Reservation queue checked automatically.', 'data': dashboard_payload(tenant)})


@require_http_methods(['POST'])
def api_renew_loan(request, loan_id):
    tenant = current_tenant(request)
    loan = get_object_or_404(Loan, id=loan_id, tenant=tenant)
    try:
        loan.renew()
        return JsonResponse({'message': 'Loan renewed.', 'data': dashboard_payload(tenant)})
    except ValidationError as exc:
        return JsonResponse({'error': '; '.join(exc.messages)}, status=400)


def dashboard_payload(tenant):
    tenants = Tenant.objects.all()
    books = Book.objects.filter(tenant=tenant)
    loans = Loan.objects.filter(tenant=tenant)
    reservations = Reservation.objects.filter(tenant=tenant)
    fines = Fine.objects.filter(tenant=tenant)
    active_loans = loans.filter(status__in=[Loan.ACTIVE, Loan.OVERDUE]).select_related('book', 'member')
    members = LibraryUser.objects.filter(tenant=tenant, role=LibraryUser.MEMBER)
    staff = LibraryUser.objects.filter(tenant=tenant, role__in=[LibraryUser.ADMIN, LibraryUser.LIBRARIAN])

    return {
        'tenant': serialize_tenant(tenant),
        'tenants': [serialize_tenant(item) for item in tenants],
        'stats': {
            'books': books.count(),
            'copies': sum(book.total_copies for book in books),
            'active_loans': active_loans.count(),
            'overdue': loans.filter(status=Loan.OVERDUE).count(),
            'reservations': reservations.filter(status__in=[Reservation.WAITING, Reservation.READY]).count(),
            'unpaid_fines': str(fines.filter(status=Fine.UNPAID).aggregate(total=Sum('amount'))['total'] or 0),
        },
        'books': [serialize_book(book) for book in books[:20]],
        'loans': [serialize_loan(loan) for loan in active_loans[:20]],
        'reservations': [serialize_reservation(item) for item in reservations.select_related('book', 'user')[:20]],
        'members': [serialize_user(member) for member in members[:20]],
        'staff': [serialize_user(user) for user in staff],
    }


def serialize_tenant(tenant):
    return {
        'id': tenant.id,
        'name': tenant.name,
        'slug': tenant.slug,
        'plan': tenant.get_subscription_plan_display(),
        'borrowingDays': tenant.borrowing_days,
        'maxRenewals': tenant.max_renewals,
        'reservationLimit': tenant.reservation_limit,
        'finePerDay': str(tenant.fine_per_day),
    }


def serialize_book(book):
    return {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'category': book.category,
        'shelfLocation': book.shelf_location,
        'totalCopies': book.total_copies,
        'availableCopies': book.available_copies,
        'queueSize': book.queue_size,
    }


def serialize_user(user):
    return {
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.get_role_display(),
        'studentId': user.student_id,
    }


def serialize_loan(loan):
    return {
        'id': loan.id,
        'book': serialize_book(loan.book),
        'member': serialize_user(loan.member),
        'dueDate': loan.due_date.isoformat(),
        'status': loan.get_status_display(),
        'renewals': loan.renewals,
    }


def serialize_reservation(reservation):
    return {
        'id': reservation.id,
        'book': serialize_book(reservation.book),
        'user': serialize_user(reservation.user),
        'queuePosition': reservation.queue_position,
        'status': reservation.get_status_display(),
        'expiryDate': reservation.expiry_date.isoformat() if reservation.expiry_date else None,
    }


def parse_json(request):
    if not request.body:
        return {}
    return json.loads(request.body.decode('utf-8'))


def first_error(form):
    for errors in form.errors.values():
        if errors:
            return errors[0]
    return 'Please check the form and try again.'
