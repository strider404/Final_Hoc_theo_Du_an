import os
import random
import django
from datetime import datetime, timedelta, time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cinema.models import Movie, Showtime
from django.utils import timezone

# 1. Clear old data
Movie.objects.all().delete()
Showtime.objects.all().delete()

# 2. Create movies list (15 movies)
movies_data = [
    {
        "title": "Dune: Part Two",
        "description": "Paul Atreides unites with the Fremen to seek revenge.",
        "duration": 165,
        "language": "English",
        "release_date": "2024-03-01",
        "poster_url": "https://picsum.photos/seed/dune2/300/400",
    },
    {
        "title": "Deadpool & Wolverine",
        "description": "Merc with a Mouth teams up with Wolverine across the multiverse.",
        "duration": 127,
        "language": "English",
        "release_date": "2024-07-25",
        "poster_url": "https://picsum.photos/seed/deadpool3/300/400",
    },
    {
        "title": "Oppenheimer",
        "description": "The story of J. Robert Oppenheimer and the atomic bomb.",
        "duration": 180,
        "language": "English",
        "release_date": "2023-07-21",
        "poster_url": "https://picsum.photos/seed/oppenheimer/300/400",
    },
    {
        "title": "Kẻ Ăn Hồn",
        "description": "Phim kinh dị Việt Nam về lời nguyền đen tối ở làng quê.",
        "duration": 109,
        "language": "Vietnamese",
        "release_date": "2023-12-15",
        "poster_url": "https://picsum.photos/seed/keanhon/300/400",
    },
    {
        "title": "Inside Out 2",
        "description": "Cảm xúc của Riley đối mặt thử thách tuổi teen.",
        "duration": 96,
        "language": "English",
        "release_date": "2024-06-14",
        "poster_url": "https://picsum.photos/seed/insideout2/300/400",
    },
    {
        "title": "The Batman",
        "description": "Batman khám phá sự thối nát của Gotham và truy tìm Riddler.",
        "duration": 176,
        "language": "English",
        "release_date": "2022-03-04",
        "poster_url": "https://picsum.photos/seed/batman2022/300/400",
    },
    {
        "title": "Spider-Man: No Way Home",
        "description": "Peter Parker đối mặt với hậu quả của việc mở đa vũ trụ.",
        "duration": 148,
        "language": "English",
        "release_date": "2021-12-17",
        "poster_url": "https://picsum.photos/seed/spidermannoway/300/400",
    },
    {
        "title": "Everything Everywhere All at Once",
        "description": "Một chủ tiệm giặt khám phá đa vũ trụ để cứu gia đình.",
        "duration": 139,
        "language": "English",
        "release_date": "2022-04-08",
        "poster_url": "https://picsum.photos/seed/everyeverything/300/400",
    },
    {
        "title": "John Wick: Chapter 4",
        "description": "Sát thủ John Wick tiếp tục cuộc chiến chống lại High Table.",
        "duration": 169,
        "language": "English",
        "release_date": "2023-03-24",
        "poster_url": "https://picsum.photos/seed/johnwick4/300/400",
    },
    {
        "title": "Top Gun: Maverick",
        "description": "Phi công Pete Mitchell trở lại huấn luyện phi đội trẻ cho nhiệm vụ nguy hiểm.",
        "duration": 130,
        "language": "English",
        "release_date": "2022-05-27",
        "poster_url": "https://picsum.photos/seed/topgun2/300/400",
    },
    {
        "title": "Parasite (Ký Sinh Trùng)",
        "description": "Gia đình nghèo xâm nhập vào cuộc sống của gia đình giàu có với những hệ lụy khôn lường.",
        "duration": 132,
        "language": "Korean",
        "release_date": "2019-05-30",
        "poster_url": "https://picsum.photos/seed/parasite/300/400",
    },
    {
        "title": "Avengers: Endgame",
        "description": "Biệt đội siêu anh hùng tập hợp để hồi sinh những người đã mất và đánh bại Thanos.",
        "duration": 181,
        "language": "English",
        "release_date": "2019-04-26",
        "poster_url": "https://picsum.photos/seed/endgame/300/400",
    },
    {
        "title": "The Dark Knight",
        "description": "Người dơi đối đầu với Joker – kẻ gieo rắc hỗn loạn ở Gotham.",
        "duration": 152,
        "language": "English",
        "release_date": "2008-07-18",
        "poster_url": "https://picsum.photos/seed/darkknight/300/400",
    },
    {
        "title": "Coco",
        "description": "Cậu bé Miguel lạc vào Vùng đất của người chết và khám phá bí mật gia đình.",
        "duration": 105,
        "language": "English/Spanish",
        "release_date": "2017-11-22",
        "poster_url": "https://picsum.photos/seed/coco/300/400",
    },
    {
        "title": "Soul",
        "description": "Một giáo viên nhạc jazz có cơ hội thứ hai sau khi lạc vào thế giới linh hồn.",
        "duration": 100,
        "language": "English",
        "release_date": "2020-12-25",
        "poster_url": "https://picsum.photos/seed/soul/300/400",
    },
]

movies = []
for data in movies_data:
    movie = Movie.objects.create(**data)
    movies.append(movie)

# 3. Create showtimes (2 per movie, tomorrow and the day after tomorrow)
now = timezone.now()
tomorrow = (now + timedelta(days=1)).date()
day_after_tomorrow = (now + timedelta(days=2)).date()

showtime_times = [time(10, 0), time(14, 30)]

rows = list('ABCDEFGHIJ')
cols = [str(i) for i in range(1, 11)]
all_seats = [f"{r}{c}" for r in rows for c in cols]

for movie in movies:
    for i, show_date_raw in enumerate([tomorrow, day_after_tomorrow]):
        show_datetime = timezone.make_aware(
            datetime.combine(show_date_raw, showtime_times[i % len(showtime_times)])
        )
        screen = f"Screen {(i % 3) + 1}"

        # Random number of booked seats (5-10)
        booked_count = random.randint(5, 10)
        sampled = random.sample(all_seats, booked_count)
        booked_str = ",".join(sampled)

        Showtime.objects.create(
            movie=movie,
            show_date=show_datetime,
            screen=screen,
            total_seats=100,
            available_seats=100 - booked_count,
            booked_seats=booked_str,
        )
