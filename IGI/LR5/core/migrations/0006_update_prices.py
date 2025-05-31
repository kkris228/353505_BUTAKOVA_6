from django.db import migrations
from decimal import Decimal

def update_prices(apps, schema_editor):
    Service = apps.get_model('core', 'Service')
    CargoType = apps.get_model('core', 'CargoType')
    
    # Устанавливаем базовую цену услуги в 50 BYN
    for service in Service.objects.all():
        service.price = Decimal('50.00')
        service.save()
    
    # Устанавливаем базовую цену за кг груза в 0.50 BYN
    for cargo_type in CargoType.objects.all():
        cargo_type.base_price = Decimal('0.50')
        cargo_type.save()

def revert_prices(apps, schema_editor):
    # Этот метод не будет ничего делать, так как мы не знаем предыдущие цены
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0005_convert_prices_to_byn'),
    ]

    operations = [
        migrations.RunPython(update_prices, revert_prices),
    ] 