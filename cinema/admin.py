from django.contrib import admin
from .models import Movie, Showtime, Booking

class MovieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'duration', 'language', 'release_date')

class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'show_date', 'screen', 'total_seats', 'available_seats')

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'showtime', 'user', 'seats', 'booked_at')

admin.site.register(Movie, MovieAdmin)
admin.site.register(Showtime, ShowtimeAdmin)
admin.site.register(Booking, BookingAdmin)
