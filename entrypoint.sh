#!/bin/bash
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@cinemax.com', 'admin1234')
    print('==> Superuser admin đã được tạo thành công!')
"
exec "$@"
