from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Driver, Vehicle, Service, VehicleBodyType, CargoType
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populate database with sample data'

    def handle(self, *args, **kwargs):
        # Создаем типы кузова
        body_types = [
            VehicleBodyType.objects.create(name='Тентованный', description='Защита груза от осадков'),
            VehicleBodyType.objects.create(name='Рефрижератор', description='Для перевозки охлажденных грузов'),
            VehicleBodyType.objects.create(name='Бортовой', description='Для перевозки габаритных грузов'),
        ]

        # Создаем типы грузов
        cargo_types = [
            CargoType.objects.create(name='Обычный', description='Стандартный груз', base_price=1000),
            CargoType.objects.create(name='Хрупкий', description='Требует осторожной перевозки', base_price=1500),
            CargoType.objects.create(name='Скоропортящийся', description='Требует специальных условий', base_price=2000),
        ]

        # Создаем водителей
        for i in range(5):
            user = User.objects.create_user(
                username=f'driver{i+1}',
                password='testpass123',
                first_name=f'Водитель{i+1}',
                last_name=f'Фамилия{i+1}'
            )
            Driver.objects.create(
                user=user,
                phone=f'+375291234{i:03d}',
                license_number=f'AB{i+1}CD{i+1}',
                experience=5+i,
                birth_date=timezone.now().date() - timedelta(days=365*30),
                is_available=True
            )

        # Создаем транспортные средства
        vehicles = [
            ('МАЗ-5440', 'AB1234-7', 2020, 20000, body_types[0]),
            ('Volvo FH', 'AB5678-7', 2021, 25000, body_types[1]),
            ('Scania R500', 'AB9012-7', 2022, 30000, body_types[2]),
        ]
        
        for model, plate, year, capacity, body_type in vehicles:
            Vehicle.objects.create(
                model=model,
                plate_number=plate,
                year=year,
                capacity=capacity,
                body_type=body_type,
                is_available=True
            )

        # Создаем услуги
        services = [
            ('Стандартная перевозка', 'Перевозка грузов по стандартному тарифу', 5000),
            ('Срочная доставка', 'Доставка в кратчайшие сроки', 8000),
            ('Перевозка негабаритных грузов', 'Перевозка крупногабаритных грузов', 12000),
        ]
        
        for name, description, price in services:
            service = Service.objects.create(
                name=name,
                description=description,
                price=price,
                is_active=True
            )
            service.cargo_types.add(*cargo_types)

        self.stdout.write(self.style.SUCCESS('База данных успешно заполнена тестовыми данными')) 