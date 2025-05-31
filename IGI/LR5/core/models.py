from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import date
from decimal import Decimal

class Organization(models.Model):
    """Организации"""
    name = models.CharField('Название', max_length=100)
    address = models.CharField('Адрес', max_length=200)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    
    class Meta:
        verbose_name = 'Организация'
        verbose_name_plural = 'Организации'
        
    def __str__(self):
        return self.name

class VehicleBodyType(models.Model):
    """Типы кузова"""
    name = models.CharField('Название', max_length=50)
    description = models.TextField('Описание', blank=True)
    
    class Meta:
        verbose_name = 'Тип кузова'
        verbose_name_plural = 'Типы кузова'
        
    def __str__(self):
        return self.name

class CargoType(models.Model):
    """Типы грузов"""
    name = models.CharField('Название', max_length=50)
    description = models.TextField('Описание', blank=True)
    base_price = models.DecimalField('Базовая цена за км', max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Тип груза'
        verbose_name_plural = 'Типы грузов'
        
    def __str__(self):
        return self.name

class Service(models.Model):
    """Услуги"""
    name = models.CharField('Название', max_length=100)
    description = models.TextField('Описание')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    cargo_types = models.ManyToManyField(CargoType, verbose_name='Типы грузов')
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создана', default=timezone.now)
    
    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        
    def __str__(self):
        return self.name

class Driver(models.Model):
    """Водители"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField('Телефон', max_length=20)
    license_number = models.CharField('Номер лицензии', max_length=20)
    experience = models.PositiveIntegerField('Стаж (лет)')
    birth_date = models.DateField('Дата рождения')
    is_available = models.BooleanField('Доступен', default=True)
    created_at = models.DateTimeField('Создан', default=timezone.now)
    photo = models.ImageField('Фотография', upload_to='drivers/', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'
        
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.license_number})"
    
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))

class Vehicle(models.Model):
    """Транспортные средства"""
    model = models.CharField('Модель', max_length=100)
    plate_number = models.CharField('Гос. номер', max_length=20, unique=True)
    year = models.PositiveIntegerField('Год выпуска')
    capacity = models.PositiveIntegerField('Грузоподъемность (кг)')
    body_type = models.ForeignKey(VehicleBodyType, on_delete=models.PROTECT, verbose_name='Тип кузова')
    is_available = models.BooleanField('Доступен', default=True)
    created_at = models.DateTimeField('Создан', default=timezone.now)
    
    class Meta:
        verbose_name = 'Транспортное средство'
        verbose_name_plural = 'Транспортные средства'
        
    def __str__(self):
        return f"{self.model} ({self.plate_number})"

class Client(models.Model):
    """Клиенты"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    phone = models.CharField('Телефон', max_length=20)
    birth_date = models.DateField('Дата рождения', default=date(2000, 1, 1))
    organization = models.ForeignKey(Organization, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Организация')
    created_at = models.DateTimeField('Создан', default=timezone.now)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

class Promotion(models.Model):
    """Промокоды"""
    code = models.CharField('Код', max_length=20, unique=True)
    description = models.TextField('Описание')
    discount_percent = models.PositiveIntegerField('Скидка (%)', validators=[MinValueValidator(1)])
    valid_from = models.DateTimeField('Действует с')
    valid_until = models.DateTimeField('Действует до')
    is_active = models.BooleanField('Активен', default=True)
    cargo_types = models.ManyToManyField(CargoType, verbose_name='Типы грузов')
    services = models.ManyToManyField(Service, verbose_name='Услуги')
    
    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        
    def __str__(self):
        return self.code

class Coupon(models.Model):
    """Купоны"""
    code = models.CharField('Код', max_length=20, unique=True)
    description = models.TextField('Описание')
    fixed_discount = models.DecimalField('Фиксированная скидка', max_digits=10, decimal_places=2)
    valid_from = models.DateTimeField('Действует с')
    valid_until = models.DateTimeField('Действует до')
    is_active = models.BooleanField('Активен', default=True)
    one_time_use = models.BooleanField('Одноразовый', default=True)
    services = models.ManyToManyField(Service, verbose_name='Услуги')
    
    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = 'Купоны'
        
    def __str__(self):
        return self.code

class Order(models.Model):
    """Заказы"""
    STATUS_CHOICES = [
        ('NEW', 'Новый'),
        ('IN_PROGRESS', 'В процессе'),
        ('COMPLETED', 'Выполнен'),
        ('CANCELLED', 'Отменен'),
    ]
    
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, verbose_name='Услуга')
    cargo_type = models.ForeignKey(CargoType, on_delete=models.PROTECT, verbose_name='Тип груза')
    weight = models.PositiveIntegerField('Вес (кг)')
    pickup_address = models.CharField('Адрес погрузки', max_length=200)
    delivery_address = models.CharField('Адрес доставки', max_length=200)
    pickup_date = models.DateTimeField('Дата погрузки')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='NEW')
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Водитель')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Транспорт')
    promotion = models.ForeignKey(Promotion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Промокод')
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Купон')
    price = models.DecimalField('Стоимость', max_digits=10, decimal_places=2, null=True, blank=True)
    rating = models.PositiveSmallIntegerField('Оценка', null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField('Отзыв', null=True, blank=True)
    created_at = models.DateTimeField('Создан', default=timezone.now)
    updated_at = models.DateTimeField('Обновлен', default=timezone.now)
    completed_at = models.DateTimeField('Выполнен', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"Заказ #{self.id} от {self.created_at.strftime('%d.%m.%Y')}"
    
    def calculate_price(self):
        """Расчет стоимости заказа"""
        # Базовая стоимость услуги
        base_price = self.service.price
        
        # Стоимость за вес (с уменьшающейся ценой за кг при большом весе)
        weight_price = Decimal('0')
        remaining_weight = self.weight
        
        if remaining_weight <= 100:  # До 100 кг - полная цена
            weight_price = Decimal(str(remaining_weight)) * self.cargo_type.base_price
        else:
            # Первые 100 кг по полной цене
            weight_price = Decimal('100') * self.cargo_type.base_price
            remaining_weight -= 100
            
            if remaining_weight <= 400:  # От 100 до 500 кг - 75% цены
                weight_price += Decimal(str(remaining_weight)) * (self.cargo_type.base_price * Decimal('0.75'))
            else:
                # От 100 до 500 кг - 75% цены
                weight_price += Decimal('400') * (self.cargo_type.base_price * Decimal('0.75'))
                remaining_weight -= 400
                
                if remaining_weight <= 500:  # От 500 до 1000 кг - 50% цены
                    weight_price += Decimal(str(remaining_weight)) * (self.cargo_type.base_price * Decimal('0.5'))
                else:
                    # От 500 до 1000 кг - 50% цены
                    weight_price += Decimal('500') * (self.cargo_type.base_price * Decimal('0.5'))
                    remaining_weight -= 500
                    
                    # Свыше 1000 кг - 25% цены
                    weight_price += Decimal(str(remaining_weight)) * (self.cargo_type.base_price * Decimal('0.25'))
        
        total = base_price + weight_price
        
        # Применяем скидку по промокоду
        if self.promotion and self.promotion.is_active:
            discount = total * (Decimal(str(self.promotion.discount_percent)) / Decimal('100'))
            total -= discount
            
        # Применяем скидку по купону
        if self.coupon and self.coupon.is_active:
            total -= self.coupon.fixed_discount
            
        return max(total, Decimal('0'))  # Стоимость не может быть отрицательной
    
    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.calculate_price()
        super().save(*args, **kwargs)

class News(models.Model):
    """Новости"""
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Краткое описание', default='')
    content = models.TextField('Содержание', default='')
    image = models.ImageField('Изображение', upload_to='news/', blank=True, null=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    
    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class FAQ(models.Model):
    """Часто задаваемые вопросы"""
    question = models.CharField('Вопрос', max_length=255)
    answer = models.TextField('Ответ')
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.question

class Job(models.Model):
    """Вакансии"""
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    requirements = models.TextField('Требования')
    salary_from = models.DecimalField('Зарплата от', max_digits=10, decimal_places=2, null=True, blank=True)
    salary_to = models.DecimalField('Зарплата до', max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Активна', default=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Вакансия'
        verbose_name_plural = 'Вакансии'
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title

class Review(models.Model):
    """Отзывы"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField('Оценка', validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    is_published = models.BooleanField('Опубликовано', default=True)
    
    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Отзыв от {self.user.get_full_name() or self.user.username}' 