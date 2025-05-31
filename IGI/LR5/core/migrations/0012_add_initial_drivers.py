from django.db import migrations
from django.contrib.auth.hashers import make_password
from datetime import date

def add_initial_drivers(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Driver = apps.get_model('core', 'Driver')
    
    # Создаем водителей
    drivers_data = [
        {
            'user': {
                'username': 'ivanov_ivan',
                'password': make_password('driver123'),
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'email': 'ivanov@example.com',
                'is_active': True
            },
            'driver': {
                'phone': '+375291234567',
                'birth_date': date(1985, 5, 15),
                'license_number': 'AB123456',
                'experience': 8,
                'is_available': True
            }
        },
        {
            'user': {
                'username': 'petrov_petr',
                'password': make_password('driver123'),
                'first_name': 'Петр',
                'last_name': 'Петров',
                'email': 'petrov@example.com',
                'is_active': True
            },
            'driver': {
                'phone': '+375292345678',
                'birth_date': date(1988, 8, 22),
                'license_number': 'CD234567',
                'experience': 6,
                'is_available': True
            }
        },
        {
            'user': {
                'username': 'sidorov_sergey',
                'password': make_password('driver123'),
                'first_name': 'Сергей',
                'last_name': 'Сидоров',
                'email': 'sidorov@example.com',
                'is_active': True
            },
            'driver': {
                'phone': '+375293456789',
                'birth_date': date(1990, 3, 10),
                'license_number': 'EF345678',
                'experience': 5,
                'is_available': True
            }
        },
        {
            'user': {
                'username': 'kozlov_konstantin',
                'password': make_password('driver123'),
                'first_name': 'Константин',
                'last_name': 'Козлов',
                'email': 'kozlov@example.com',
                'is_active': True
            },
            'driver': {
                'phone': '+375294567890',
                'birth_date': date(1983, 11, 5),
                'license_number': 'GH456789',
                'experience': 12,
                'is_available': True
            }
        },
        {
            'user': {
                'username': 'novikov_nikolay',
                'password': make_password('driver123'),
                'first_name': 'Николай',
                'last_name': 'Новиков',
                'email': 'novikov@example.com',
                'is_active': True
            },
            'driver': {
                'phone': '+375295678901',
                'birth_date': date(1987, 7, 28),
                'license_number': 'IJ567890',
                'experience': 7,
                'is_available': True
            }
        }
    ]
    
    for driver_data in drivers_data:
        # Создаем пользователя
        user = User.objects.create(**driver_data['user'])
        
        # Создаем профиль водителя
        driver_profile = driver_data['driver']
        driver_profile['user'] = user
        Driver.objects.create(**driver_profile)

def remove_initial_drivers(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Driver = apps.get_model('core', 'Driver')
    
    usernames = ['ivanov_ivan', 'petrov_petr', 'sidorov_sergey', 'kozlov_konstantin', 'novikov_nikolay']
    
    # Удаляем водителей и их пользователей
    Driver.objects.filter(user__username__in=usernames).delete()
    User.objects.filter(username__in=usernames).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0011_add_initial_faqs'),
    ]

    operations = [
        migrations.RunPython(add_initial_drivers, remove_initial_drivers),
    ] 