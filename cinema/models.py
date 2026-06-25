from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    poster_url = models.URLField(blank=True, null=True)
    poster_image = models.ImageField(upload_to='posters/', blank=True, null=True)
    duration = models.IntegerField(help_text="Duration in minutes")
    language = models.CharField(max_length=100, blank=True)
    release_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    show_date = models.DateTimeField()
    screen = models.CharField(max_length=10)
    total_seats = models.IntegerField(default=100)
    available_seats = models.IntegerField(default=100)
    booked_seats = models.TextField(blank=True, default="")

    @property
    def is_past(self):
        return self.show_date < timezone.now()

    def __str__(self):
        return f"{self.movie.title} - {self.show_date}"

class Booking(models.Model):
    PENDING = 'PENDING'
    CONFIRMED = 'CONFIRMED'
    CANCELLED = 'CANCELLED'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (CANCELLED, 'Cancelled'),
    ]
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    seats = models.IntegerField(default=1)
    seat_numbers = models.TextField(blank=True, default="")
    total_price = models.IntegerField(default=0)
    booked_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=CONFIRMED,
    )

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.showtime}"
        return f"Anonymous - {self.showtime}"
