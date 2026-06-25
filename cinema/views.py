import json
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.mail import send_mail
from django.db.models import Q, Sum
from django.contrib.auth.models import User
from .models import Movie, Showtime, Booking
from .forms import UserAdminForm, BookingAdminForm


class StyledUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


def register_user(request):
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}!")
            return redirect('movie_list')
    else:
        form = StyledUserCreationForm()
    return render(request, 'cinema/register.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        form = StyledAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Logged in as {user.username}.")
            return redirect('movie_list')
    else:
        form = StyledAuthenticationForm()
    return render(request, 'cinema/login.html', {'form': form})


def logout_user(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.success(request, f"Logged out {username}.")
    else:
        messages.error(request, "Not logged in.")
    return redirect('movie_list')


def movie_list(request):
    query = request.GET.get('q', '')
    if query:
        movies_qs = Movie.objects.filter(title__icontains=query)
    else:
        movies_qs = Movie.objects.all()
    paginator = Paginator(movies_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'cinema/movie_list.html', {
        'movies': page_obj,
        'page_obj': page_obj,
        'query': query,
    })


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    showtimes = movie.showtime_set.all()
    return render(request, 'cinema/movie_detail.html', {'movie': movie, 'showtimes': showtimes})


def _get_seat_price(row_letter):
    if row_letter in 'ABC':
        return 70000
    if row_letter in 'DEFGH':
        return 90000
    # I, J
    return 160000


@login_required(login_url='login')
def seat_selection(request, showtime_id):
    showtime = get_object_or_404(Showtime, pk=showtime_id)

    # true booked seats from CONFIRMED bookings only
    valid_bookings = Booking.objects.filter(showtime=showtime, status='CONFIRMED')
    booked = []
    for booking in valid_bookings:
        if booking.seat_numbers:
            seats = [s.strip() for s in booking.seat_numbers.split(',') if s.strip()]
            booked.extend(seats)

    rows = list('ABCDEFGHIJ')
    cols = list(range(1, 11))

    if request.method == 'POST':
        selected_str = request.POST.get('selected_seats', '')
        selected = [s.strip() for s in selected_str.split(',') if s.strip()]
        already_booked_set = set(booked)
        selected_set = set(selected)
        new_seats = sorted(selected_set - already_booked_set)

        if not new_seats:
            messages.error(request, "Không có ghế mới được chọn.")
            return render(request, 'cinema/seat_selection.html', {
                'showtime': showtime,
                'booked_seats': booked,
                'booked_seats_json': json.dumps(booked),
                'rows': rows,
                'cols': cols,
            })

        seats_count = len(new_seats)
        if seats_count > showtime.available_seats:
            messages.error(request, "Không đủ ghế trống.")
            return render(request, 'cinema/seat_selection.html', {
                'showtime': showtime,
                'booked_seats': booked,
                'booked_seats_json': json.dumps(booked),
                'rows': rows,
                'cols': cols,
            })

        # Calculate total price (backend‑computed for security)
        total_price = 0
        for seat in new_seats:
            row_letter = seat[0].upper()  # first character of seat id (e.g. A3 -> 'A')
            total_price += _get_seat_price(row_letter)

        # Store checkout data in session
        request.session['checkout_seats'] = ','.join(new_seats)
        request.session['checkout_total'] = total_price
        request.session['checkout_showtime_id'] = showtime_id

        return redirect('checkout', showtime_id=showtime_id)

    return render(request, 'cinema/seat_selection.html', {
        'showtime': showtime,
        'booked_seats': booked,
        'booked_seats_json': json.dumps(booked),
        'rows': rows,
        'cols': cols,
    })


@login_required(login_url='login')
def checkout_view(request, showtime_id):
    showtime = get_object_or_404(Showtime, pk=showtime_id)
    session = request.session

    seats_str = session.get('checkout_seats')
    total = session.get('checkout_total')
    session_showtime_id = session.get('checkout_showtime_id')

    if not seats_str or total is None or session_showtime_id != showtime_id:
        messages.error(request, "Không có dữ liệu đặt vé. Vui lòng chọn ghế lại.")
        return redirect('seat_selection', showtime_id=showtime_id)

    seats = [s.strip() for s in seats_str.split(',') if s.strip()]

    if request.method == 'POST':
        # Confirm payment
        booked = []
        if showtime.booked_seats:
            booked = [s.strip() for s in showtime.booked_seats.split(',') if s.strip()]

        already_booked_set = set(booked)
        selected_set = set(seats)

        # Check for seat collision (seat just booked by someone else)
        if selected_set & already_booked_set:
            messages.error(request, "Rất tiếc, ghế bạn chọn vừa có người đặt thành công. Vui lòng chọn ghế khác!")
            # Clear session so the stale data cannot be reused
            del session['checkout_seats']
            del session['checkout_total']
            del session['checkout_showtime_id']
            return redirect('seat_selection', showtime_id=showtime_id)

        new_seats = sorted(selected_set - already_booked_set)  # should equal seats as there is no overlap

        if not new_seats:
            messages.error(request, "Không có ghế mới.")
            return redirect('seat_selection', showtime_id=showtime_id)

        if len(new_seats) > showtime.available_seats:
            messages.error(request, "Không đủ ghế trống.")
            return redirect('seat_selection', showtime_id=showtime_id)

        all_booked = sorted(already_booked_set | selected_set)
        showtime.booked_seats = ','.join(all_booked)
        showtime.available_seats -= len(new_seats)
        showtime.save()

        Booking.objects.create(
            showtime=showtime,
            user=request.user,
            seats=len(new_seats),
            seat_numbers=','.join(new_seats),
            total_price=total,
        )

        # Send confirmation email (console backend)
        if request.user.email:
            send_mail(
                "Vé xem phim Cinemax",
                f"Phim: {showtime.movie.title}\n"
                f"Giờ chiếu: {showtime.show_date.strftime('%d/%m/%Y %H:%M')}\n"
                f"Ghế đã chọn: {', '.join(new_seats)}\n"
                f"Tổng tiền: {total} VNĐ",
                "noreply@cinemax.com",
                [request.user.email],
            )

        # Clear session data
        del session['checkout_seats']
        del session['checkout_total']
        del session['checkout_showtime_id']

        messages.success(request, f"Thanh toán thành công {total} VNĐ cho {len(new_seats)} ghế.")
        return redirect('profile')

    # GET - show checkout summary
    return render(request, 'cinema/checkout.html', {
        'showtime': showtime,
        'seats': seats,
        'total_price': total,
    })


@login_required(login_url='login')
def profile_view(request):
    if request.method == 'POST' and request.POST.get('action') == 'update_profile':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        messages.success(request, "Cập nhật thông tin thành công!")
        return redirect('profile')

    bookings = Booking.objects.filter(user=request.user).order_by('-booked_at')
    return render(request, 'cinema/profile.html', {
        'bookings': bookings,
        'user': request.user,
    })


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Mật khẩu đã được thay đổi thành công.")
            return redirect('profile')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'cinema/change_password.html', {'form': form})


@login_required(login_url='login')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.user != request.user:
        messages.error(request, "Bạn không sở hữu vé này.")
        return redirect('profile')

    if booking.status == 'CANCELLED':
        messages.error(request, "Vé này đã bị hủy.")
        return redirect('profile')

    if booking.showtime.is_past:
        messages.error(request, "Suất chiếu đã diễn ra, không thể hủy.")
        return redirect('profile')

    booking.status = Booking.CANCELLED
    booking.save()

    showtime = booking.showtime
    showtime.available_seats += booking.seats

    if booking.seat_numbers:
        seats_to_remove = [s.strip() for s in booking.seat_numbers.split(',') if s.strip()]
        current_booked = showtime.booked_seats
        current_list = [s.strip() for s in current_booked.split(',') if s.strip()] if current_booked else []
        updated_list = [s for s in current_list if s not in seats_to_remove]
        showtime.booked_seats = ','.join(updated_list)
    showtime.save()

    messages.success(request, "Đã hủy vé thành công.")
    return redirect('profile')


# ---------- ADMIN VIEWS (superuser only) ----------

@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    total_revenue = Booking.objects.filter(status=Booking.CONFIRMED).aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_tickets = Booking.objects.filter(status=Booking.CONFIRMED).count()
    total_movies = Movie.objects.count()
    recent_bookings = Booking.objects.all().order_by('-booked_at')[:10]
    context = {
        'total_revenue': total_revenue,
        'total_tickets': total_tickets,
        'total_movies': total_movies,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'cinema/admin_dashboard.html', context)


@user_passes_test(lambda u: u.is_superuser)
def admin_users(request):
    users = User.objects.all()
    return render(request, 'cinema/admin_users.html', {'users': users})


@user_passes_test(lambda u: u.is_superuser)
def admin_user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        form = UserAdminForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật người dùng thành công.')
            return redirect('admin_users')
    else:
        form = UserAdminForm(instance=user)
    return render(request, 'cinema/admin_form.html', {
        'form': form,
        'title': f'Chỉnh sửa người dùng {user.username}',
    })


@user_passes_test(lambda u: u.is_superuser)
def admin_bookings(request):
    bookings = Booking.objects.all().order_by('-booked_at')
    return render(request, 'cinema/admin_bookings.html', {'bookings': bookings})


@user_passes_test(lambda u: u.is_superuser)
def admin_booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.method == 'POST':
        form = BookingAdminForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cập nhật booking thành công.')
            return redirect('admin_bookings')
    else:
        form = BookingAdminForm(instance=booking)
    return render(request, 'cinema/admin_form.html', {
        'form': form,
        'title': f'Chỉnh sửa booking #{booking.id}',
    })
