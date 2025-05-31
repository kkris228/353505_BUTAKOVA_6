from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db.models import Avg, Count
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import re
from .models import (
    Organization, Driver, Vehicle, Client, Order, 
    Promotion, CargoType, Service, VehicleBodyType,
    Coupon
)

# Отменяем стандартную регистрацию User
admin.site.unregister(User)

# Регистрируем свою версию админки для User
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

def validate_phone(value):
    """
    +375 (29) 123-45-67
    +375291234567
    375291234567
    8 029 123-45-67
    """
    # Удаляем все не цифры для проверки длины
    cleaned_number = re.sub(r'\D', '', value)
    
    # Проверяем длину (9 цифр для номера + 3 цифры код страны)
    if len(cleaned_number) not in [12, 13]:  # 12 для формата 375... и 13 для +375...
        raise ValidationError('Номер телефона должен содержать 12 или 13 цифр')
    
    # Проверяем формат с помощью регулярного выражения
    patterns = [
        r'^\+375 \(\d{2}\) \d{3}-\d{2}-\d{2}$',  # +375 (29) 123-45-67
        r'^\+375\d{9}$',                          # +375291234567
        r'^375\d{9}$',                            # 375291234567
        r'^8 0\d{2} \d{3}-\d{2}-\d{2}$'          # 8 029 123-45-67
    ]
    
    if not any(re.match(pattern, value) for pattern in patterns):
        raise ValidationError(
            'Неверный формат номера. Допустимые форматы:\n'
            '+375 (29) 123-45-67\n'
            '+375291234567\n'
            '375291234567\n'
            '8 029 123-45-67'
        )

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'email')
    search_fields = ('name', 'address', 'phone', 'email')
    ordering = ('name',)
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

@admin.register(VehicleBodyType)
class VehicleBodyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_vehicles_count')
    search_fields = ('name', 'description')
    
    def get_vehicles_count(self, obj):
        return Vehicle.objects.filter(body_type=obj).count()
    get_vehicles_count.short_description = 'Количество транспорта'

@admin.register(CargoType)
class CargoTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'get_orders_count', 'get_avg_weight')
    search_fields = ('name', 'description')
    
    def get_orders_count(self, obj):
        return Order.objects.filter(cargo_type=obj).count()
    get_orders_count.short_description = 'Количество заказов'
    
    def get_avg_weight(self, obj):
        avg = Order.objects.filter(cargo_type=obj).aggregate(Avg('weight'))['weight__avg']
        return round(avg, 2) if avg else 0
    get_avg_weight.short_description = 'Средний вес (кг)'

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'get_orders_count')
    list_filter = ('is_active', 'cargo_types')
    search_fields = ('name', 'description')
    filter_horizontal = ('cargo_types',)
    
    def get_orders_count(self, obj):
        return Order.objects.filter(service=obj).count()
    get_orders_count.short_description = 'Количество заказов'

@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'license_number', 'experience', 'age', 'is_available', 'created_at')
    list_filter = ('is_available', 'experience')
    search_fields = ('user__first_name', 'user__last_name', 'phone', 'license_number')
    ordering = ('-created_at',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'ФИО'
    
    def age(self, obj):
        return obj.age()
    age.short_description = 'Возраст'
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('model', 'plate_number', 'year', 'capacity', 'body_type', 'is_available', 'created_at')
    list_filter = ('is_available', 'body_type', 'year')
    search_fields = ('model', 'plate_number')
    ordering = ('-created_at',)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'phone', 'birth_date', 'get_organization', 'get_orders_count', 'created_at')
    list_filter = ('organization', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'phone', 'organization__name')
    ordering = ('-created_at',)
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'ФИО'
    
    def get_organization(self, obj):
        return obj.organization.name if obj.organization else '-'
    get_organization.short_description = 'Организация'
    
    def get_orders_count(self, obj):
        return Order.objects.filter(client=obj).count()
    get_orders_count.short_description = 'Количество заказов'
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        validate_phone(phone)
        return phone

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'valid_from', 'valid_until', 'is_active')
    list_filter = ('is_active', 'cargo_types', 'services')
    search_fields = ('code', 'description')
    filter_horizontal = ('cargo_types', 'services')

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'fixed_discount', 'valid_from', 'valid_until', 'is_active', 'one_time_use')
    list_filter = ('is_active', 'one_time_use', 'services')
    search_fields = ('code', 'description')
    filter_horizontal = ('services',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'service', 'cargo_type', 'weight', 'price', 'status', 'created_at')
    list_filter = ('status', 'service', 'cargo_type', 'created_at')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'pickup_address', 'delivery_address')
    ordering = ('-created_at',)
    readonly_fields = ('price',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('client', 'service', 'cargo_type', 'weight')
        }),
        ('Адреса', {
            'fields': ('pickup_address', 'delivery_address', 'pickup_date')
        }),
        ('Исполнение', {
            'fields': ('driver', 'vehicle', 'status', 'completed_at')
        }),
        ('Стоимость', {
            'fields': ('promotion', 'coupon', 'price')
        }),
    ) 