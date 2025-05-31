from django.db import migrations

def add_initial_vehicles(apps, schema_editor):
    Vehicle = apps.get_model('core', 'Vehicle')
    VehicleBodyType = apps.get_model('core', 'VehicleBodyType')
    
    # Получаем или создаем типы кузова
    tent_type = VehicleBodyType.objects.get_or_create(
        name='Тентованный',
        defaults={'description': 'Защита груза от осадков'}
    )[0]
    
    ref_type = VehicleBodyType.objects.get_or_create(
        name='Рефрижератор',
        defaults={'description': 'Для перевозки охлажденных грузов'}
    )[0]
    
    bort_type = VehicleBodyType.objects.get_or_create(
        name='Бортовой',
        defaults={'description': 'Для перевозки габаритных грузов'}
    )[0]
    
    izot_type = VehicleBodyType.objects.get_or_create(
        name='Изотермический',
        defaults={'description': 'Для перевозки грузов с поддержанием постоянной температуры'}
    )[0]
    
    # Создаем транспортные средства
    vehicles = [
        {
            'model': 'Mercedes-Benz Actros 1841',
            'plate_number': 'AB7777-7',
            'year': 2023,
            'capacity': 22000,
            'body_type': tent_type,
            'is_available': True
        },
        {
            'model': 'Volvo FH16 750',
            'plate_number': 'AB8888-7',
            'year': 2022,
            'capacity': 25000,
            'body_type': ref_type,
            'is_available': True
        },
        {
            'model': 'Scania S730',
            'plate_number': 'AB9999-7',
            'year': 2023,
            'capacity': 24000,
            'body_type': bort_type,
            'is_available': True
        },
        {
            'model': 'DAF XF 480',
            'plate_number': 'AB1111-7',
            'year': 2022,
            'capacity': 20000,
            'body_type': izot_type,
            'is_available': True
        },
        {
            'model': 'MAN TGX 18.500',
            'plate_number': 'AB2222-7',
            'year': 2023,
            'capacity': 21000,
            'body_type': tent_type,
            'is_available': True
        },
        {
            'model': 'Renault T520',
            'plate_number': 'AB3333-7',
            'year': 2022,
            'capacity': 23000,
            'body_type': ref_type,
            'is_available': True
        },
        {
            'model': 'IVECO S-WAY',
            'plate_number': 'AB4444-7',
            'year': 2023,
            'capacity': 19000,
            'body_type': bort_type,
            'is_available': True
        }
    ]
    
    for vehicle_data in vehicles:
        Vehicle.objects.create(**vehicle_data)

def remove_initial_vehicles(apps, schema_editor):
    Vehicle = apps.get_model('core', 'Vehicle')
    plate_numbers = [
        'AB7777-7', 'AB8888-7', 'AB9999-7', 'AB1111-7',
        'AB2222-7', 'AB3333-7', 'AB4444-7'
    ]
    Vehicle.objects.filter(plate_number__in=plate_numbers).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_add_initial_drivers'),
    ]

    operations = [
        migrations.RunPython(add_initial_vehicles, remove_initial_vehicles),
    ] 