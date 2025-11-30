#!/bin/sh

# Migracje
python manage.py migrate --noinput


# Tworzenie superusera jeśli nie istnieje
python manage.py shell <<EOF

# Tworzenie superusera, wpisz swoje dane tutaj
# Hasło można zmienić w panelu admina po pierwszym zalogowaniu
username = "student" 
password = "studentpass"


from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, "", password)
EOF

# Start serwera
exec python manage.py runserver 0.0.0.0:8000