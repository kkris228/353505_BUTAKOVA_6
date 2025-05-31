from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import Driver
import random

class Command(BaseCommand):
    help = 'Updates drivers with random realistic names'

    def handle(self, *args, **options):
        first_names = [
            'Александр', 'Михаил', 'Иван', 'Дмитрий', 'Андрей', 'Николай', 'Сергей',
            'Владимир', 'Артём', 'Алексей', 'Максим', 'Евгений', 'Роман', 'Виктор',
            'Павел', 'Денис', 'Игорь', 'Антон', 'Олег', 'Константин'
        ]
        
        last_names = [
            'Иванов', 'Смирнов', 'Кузнецов', 'Попов', 'Васильев', 'Петров', 'Соколов',
            'Михайлов', 'Новиков', 'Федоров', 'Морозов', 'Волков', 'Алексеев', 'Лебедев',
            'Семенов', 'Егоров', 'Павлов', 'Козлов', 'Степанов', 'Николаев'
        ]

        drivers = Driver.objects.all()
        for driver in drivers:
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            if driver.user:
                user = driver.user
                user.first_name = first_name
                user.last_name = last_name
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Updated driver name to {first_name} {last_name}'))
            
        self.stdout.write(self.style.SUCCESS('Successfully updated all driver names')) 