from django.urls import path
from . import views

urlpatterns = [
    path('', views.movie_list, name='movie_list'),
    path('<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('<int:showtime_id>/seats/', views.seat_selection, name='seat_selection'),
    path('checkout/<int:showtime_id>/', views.checkout_view, name='checkout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # Admin dashboard routes
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/users/<int:user_id>/edit/', views.admin_user_edit, name='admin_user_edit'),
    path('dashboard/bookings/', views.admin_bookings, name='admin_bookings'),
    path('dashboard/bookings/<int:booking_id>/edit/', views.admin_booking_edit, name='admin_booking_edit'),
]
