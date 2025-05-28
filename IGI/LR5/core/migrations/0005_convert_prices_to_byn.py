from django.db import migrations
from decimal import Decimal

def convert_to_byn(apps, schema_editor):
    # Конвертация цен в заказах
    Order = apps.get_model('core', 'Order')
    for order in Order.objects.all():
        if order.price:
            order.price = Decimal(float(order.price) / 30).quantize(Decimal('0.01'))
            order.save()
    
    # Конвертация базовых цен типов грузов
    CargoType = apps.get_model('core', 'CargoType')
    for cargo_type in CargoType.objects.all():
        cargo_type.base_price = Decimal(float(cargo_type.base_price) / 30).quantize(Decimal('0.01'))
        cargo_type.save()
    
    # Конвертация цен услуг
    Service = apps.get_model('core', 'Service')
    for service in Service.objects.all():
        service.price = Decimal(float(service.price) / 30).quantize(Decimal('0.01'))
        service.save()
    
    # Конвертация фиксированных скидок в купонах
    Coupon = apps.get_model('core', 'Coupon')
    for coupon in Coupon.objects.all():
        coupon.fixed_discount = Decimal(float(coupon.fixed_discount) / 30).quantize(Decimal('0.01'))
        coupon.save()

def convert_to_rub(apps, schema_editor):
    # Обратная конвертация цен в заказах (для отката миграции)
    Order = apps.get_model('core', 'Order')
    for order in Order.objects.all():
        if order.price:
            order.price = Decimal(float(order.price) * 30).quantize(Decimal('0.01'))
            order.save()
    
    # Обратная конвертация базовых цен типов грузов
    CargoType = apps.get_model('core', 'CargoType')
    for cargo_type in CargoType.objects.all():
        cargo_type.base_price = Decimal(float(cargo_type.base_price) * 30).quantize(Decimal('0.01'))
        cargo_type.save()
    
    # Обратная конвертация цен услуг
    Service = apps.get_model('core', 'Service')
    for service in Service.objects.all():
        service.price = Decimal(float(service.price) * 30).quantize(Decimal('0.01'))
        service.save()
    
    # Обратная конвертация фиксированных скидок в купонах
    Coupon = apps.get_model('core', 'Coupon')
    for coupon in Coupon.objects.all():
        coupon.fixed_discount = Decimal(float(coupon.fixed_discount) * 30).quantize(Decimal('0.01'))
        coupon.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0004_order_feedback_order_rating'),
    ]

    operations = [
        migrations.RunPython(convert_to_byn, convert_to_rub),
    ] 