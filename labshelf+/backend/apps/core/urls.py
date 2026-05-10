from django.urls import path

from . import views

urlpatterns = [
    path('', views.app_shell, name='app-shell'),
    path('api/dashboard/', views.api_dashboard, name='api-dashboard'),
    path('api/tenant/', views.api_switch_tenant, name='api-switch-tenant'),
    path('api/books/', views.api_create_book, name='api-create-book'),
    path('api/members/', views.api_create_member, name='api-create-member'),
    path('api/loans/', views.api_checkout_book, name='api-checkout-book'),
    path('api/loans/<int:loan_id>/return/', views.api_return_loan, name='api-return-loan'),
    path('api/loans/<int:loan_id>/renew/', views.api_renew_loan, name='api-renew-loan'),
    path('api/reservations/', views.api_reserve_book, name='api-reserve-book'),
]
