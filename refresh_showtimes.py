import os
import django
from django.utils import timezone
from datetime import timedelta, datetime, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cinema.models import Movie, Showtime

def refresh_showtimes():
    movies = Movie.objects.all()
    now = timezone.now()
    for movie in movies:
        for day_offset in range(1, 4):          # tomorrow, the day after, two days later
            target_day = now + timedelta(days=day_offset)
            target_date = target_day.date()
            # two slots per day
            for slot_number, (hour, minute) in enumerate([(14, 0), (20, 0)], start=1):
                showtime_dt = timezone.make_aware(datetime.combine(target_date, time(hour, minute)))
                if Showtime.objects.filter(movie=movie, show_date=showtime_dt).exists():
                    continue
                Showtime.objects.create(
                    movie=movie,
                    show_date=showtime_dt,
                    screen=str(slot_number),
                    total_seats=100,
                    available_seats=100,
                    booked_seats='',
                )

if __name__ == '__main__':
    refresh_showtimes()
    print('Showtimes refreshed.')
