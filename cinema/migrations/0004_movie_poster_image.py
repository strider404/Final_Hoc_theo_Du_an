from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cinema', '0003_showtime_booked_seats'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='poster_image',
            field=models.ImageField(blank=True, null=True, upload_to='posters/'),
        ),
    ]
