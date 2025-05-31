from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Avg, Count, Sum, Q
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.functions import ExtractMonth
from django.contrib.auth import login
from datetime import date, datetime
from django import forms
import json

from .models import (
    Organization, Driver, Vehicle, Client, Order, 
    Promotion, CargoType, Service, VehicleBodyType,
    Coupon, News, FAQ, Job, Review
)
from .forms import (
    ClientRegistrationForm, VehicleForm, DriverForm,
    NewsForm
)
from .services import get_random_joke

def get_month_calendar(year=2025, month=5):
    # Названия месяцев
    month_names = [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ]
    
    # Определяем количество дней в месяце
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    # Проверка на високосный год
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_month[2] = 29
    
    # Определяем день недели для 1-го числа месяца
    # Используем формулу Зеллера
    if month < 3:
        month += 12
        year -= 1
    k = year % 100
    j = year // 100
    h = (1 + ((13 * (month + 1)) // 5) + k + (k // 4) + (j // 4) - (2 * j)) % 7
    # Преобразуем в формат где понедельник = 0, воскресенье = 6
    first_day = (h + 5) % 7
    
    # Формируем календарь
    cal_str = "Пн   Вт   Ср   Чт   Пт   Сб   Вс\n"
    
    # Добавляем отступы для первой недели
    current_pos = 0
    if first_day > 0:
        cal_str += "     " * first_day
        current_pos = first_day
    
    # Добавляем дни
    for day in range(1, days_in_month[month % 12 or 12] + 1):
        cal_str += f"{day:2}   "
        current_pos += 1
        if current_pos == 7:
            cal_str = cal_str.rstrip() + "\n"
            current_pos = 0
    
    return cal_str.rstrip(), f"Календарь - {month_names[month % 12 - 1]} {year}"

def get_orders_statistics():
    from .models import Order
    
    # Получаем статистику по статусам заказов
    status_stats = Order.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')
    
    # Форматируем данные для диаграммы
    labels = []
    data = []
    colors = {
        'NEW': '#f1c40f',        # Желтый
        'IN_PROGRESS': '#3498db', # Синий
        'COMPLETED': '#2ecc71',   # Зеленый
        'CANCELLED': '#e74c3c'    # Красный
    }
    background_colors = []
    
    total_orders = sum(stat['count'] for stat in status_stats)
    
    for stat in status_stats:
        status_display = dict(Order.STATUS_CHOICES)[stat['status']]
        percentage = (stat['count'] / total_orders) * 100 if total_orders > 0 else 0
        labels.append(f"{status_display} ({percentage:.1f}%)")
        data.append(stat['count'])
        background_colors.append(colors.get(stat['status'], '#95a5a6'))
    
    return {
        'labels': labels,
        'data': data,
        'colors': background_colors
    }

def get_cargo_statistics():
    from .models import Order
    
    # Получаем статистику по типам грузов
    cargo_stats = Order.objects.values('cargo_type__name').annotate(
        count=Count('id'),
        total_weight=Sum('weight'),
        avg_cost=Avg('price')
    ).order_by('-count')
    
    # Форматируем данные для диаграммы
    labels = []
    data = []
    colors = [
        '#2ecc71',  # Зеленый
        '#3498db',  # Синий
        '#9b59b6',  # Фиолетовый
        '#f1c40f',  # Желтый
        '#e74c3c',  # Красный
        '#1abc9c',  # Бирюзовый
        '#e67e22'   # Оранжевый
    ]
    
    total_orders = sum(stat['count'] for stat in cargo_stats)
    
    for i, stat in enumerate(cargo_stats):
        percentage = (stat['count'] / total_orders) * 100 if total_orders > 0 else 0
        labels.append(f"{stat['cargo_type__name']} ({percentage:.1f}%)")
        data.append(stat['count'])
    
    return {
        'labels': labels,
        'data': data,
        'colors': colors[:len(data)]  # Берем только нужное количество цветов
    }

class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем статистику
        context['total_orders'] = Order.objects.count()
        context['active_drivers'] = Driver.objects.filter(is_available=True).count()
        context['available_vehicles'] = Vehicle.objects.filter(is_available=True).count()
        
        # Добавляем календарь
        calendar_text, calendar_title = get_month_calendar(2025, 5)
        context['calendar_text'] = calendar_text
        context['calendar_title'] = calendar_title
        
        return context

class OrderListView(LoginRequiredMixin, ListView):
    """Список заказов"""
    model = Order
    template_name = 'core/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'driver'):
            return queryset.filter(driver=self.request.user.driver)
        elif hasattr(self.request.user, 'client'):
            return queryset.filter(client=self.request.user.client)
        elif self.request.user.is_superuser:
            return queryset
        return Order.objects.none()

class OrderDetailView(LoginRequiredMixin, DetailView):
    """Детали заказа"""
    model = Order
    template_name = 'core/order_detail.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, 'driver'):
            return queryset.filter(driver=self.request.user.driver)
        elif hasattr(self.request.user, 'client'):
            return queryset.filter(client=self.request.user.client)
        elif self.request.user.is_superuser:
            return queryset
        return Order.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        
        # Добавляем информацию о статусе заказа
        context['status_class'] = {
            'NEW': 'warning',
            'IN_PROGRESS': 'info',
            'COMPLETED': 'success',
            'CANCELLED': 'danger'
        }.get(order.status, 'secondary')
        
        # Добавляем информацию о стоимости
        if order.price:
            context['cost_per_km'] = round(order.price / max(order.distance, 1), 2) if hasattr(order, 'distance') else None
            context['cost_per_kg'] = round(order.price / max(order.weight, 1), 2)
        
        return context

class OrderCreateView(LoginRequiredMixin, CreateView):
    """Создание заказа"""
    model = Order
    template_name = 'core/order_form.html'
    fields = [
        'service',
        'cargo_type',
        'weight',
        'pickup_address',
        'delivery_address',
        'pickup_date'
    ]
    success_url = reverse_lazy('order-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.request.user.is_superuser:
            # Добавляем поля для администратора
            form.fields.update({
                'driver': forms.ModelChoiceField(
                    queryset=Driver.objects.filter(is_available=True),
                    required=False,
                    label='Водитель'
                ),
                'vehicle': forms.ModelChoiceField(
                    queryset=Vehicle.objects.filter(is_available=True),
                    required=False,
                    label='Транспорт'
                ),
                'status': forms.ChoiceField(
                    choices=Order.STATUS_CHOICES,
                    initial='NEW',
                    label='Статус'
                ),
                'price': forms.DecimalField(
                    max_digits=10,
                    decimal_places=2,
                    required=False,
                    label='Стоимость'
                )
            })
        return form

    def form_valid(self, form):
        order = form.save(commit=False)
        if hasattr(self.request.user, 'client'):
            order.client = self.request.user.client
        # Рассчитываем стоимость заказа
        order.price = order.calculate_price()
        order.save()
        messages.success(self.request, 'Заказ успешно создан!')
        return super().form_valid(form)

class DriverListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список водителей"""
    model = Driver
    template_name = 'core/driver_list.html'
    context_object_name = 'drivers'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по доступности
        availability = self.request.GET.get('availability')
        if availability in ['0', '1']:
            queryset = queryset.filter(is_available=bool(int(availability)))
            
        # Фильтрация по минимальному стажу
        min_experience = self.request.GET.get('min_experience')
        if min_experience:
            queryset = queryset.filter(experience__gte=int(min_experience))
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика
        drivers = Driver.objects.all()
        context['avg_age'] = round(sum(driver.age() for driver in drivers) / max(len(drivers), 1), 1)
        context['avg_experience'] = round(drivers.aggregate(Avg('experience'))['experience__avg'] or 0, 1)
        context['available_count'] = drivers.filter(is_available=True).count()
        
        return context

class VehicleListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Список транспортных средств"""
    model = Vehicle
    template_name = 'core/vehicle_list.html'
    context_object_name = 'vehicles'

    def test_func(self):
        return self.request.user.is_superuser

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Фильтрация по типу кузова
        body_type = self.request.GET.get('body_type')
        if body_type:
            queryset = queryset.filter(body_type_id=body_type)
            
        # Фильтрация по доступности
        availability = self.request.GET.get('availability')
        if availability in ['0', '1']:
            queryset = queryset.filter(is_available=bool(int(availability)))
            
        # Фильтрация по минимальной грузоподъемности
        min_capacity = self.request.GET.get('min_capacity')
        if min_capacity:
            queryset = queryset.filter(capacity__gte=int(min_capacity))
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Типы кузовов для фильтра
        context['body_types'] = VehicleBodyType.objects.all()
        
        # Статистика
        vehicles = Vehicle.objects.all()
        current_year = timezone.now().year
        context['total_capacity'] = vehicles.aggregate(Sum('capacity'))['capacity__sum'] or 0
        context['avg_age'] = round(current_year - vehicles.aggregate(Avg('year'))['year__avg'] or current_year, 1) if vehicles.exists() else 0
        context['available_count'] = vehicles.filter(is_available=True).count()
        
        return context

class StatisticsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Статистика заказов"""
    template_name = 'core/statistics.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Основные показатели
        orders = Order.objects.all()
        context['total_orders'] = orders.count()
        
        # Финансовые показатели
        total_revenue = orders.aggregate(total=Sum('price'))['total'] or 0
        context['total_revenue'] = round(total_revenue, 2)
        context['avg_order_cost'] = round(total_revenue / max(orders.count(), 1), 2)
        
        # Статистика по типам грузов
        context['cargo_stats'] = (
            Order.objects.values('cargo_type__name')
            .annotate(
                order_count=Count('id'),
                total_weight=Sum('weight'),
                avg_cost=Avg('price')
            )
            .order_by('-order_count')
        )
        
        # Данные для графика по месяцам
        current_year = timezone.now().year
        months_data = (
            Order.objects.filter(created_at__year=current_year)
            .annotate(month=ExtractMonth('created_at'))
            .values('month')
            .annotate(
                count=Count('id'),
                revenue=Sum('price')
            )
            .order_by('month')
        )
        
        # Подготовка данных для графика
        month_names = [
            'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
            'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
        ]
        
        months = []
        orders_count = []
        
        for month in range(1, 13):
            month_data = next((item for item in months_data if item['month'] == month), None)
            months.append(f'"{month_names[month - 1]}"')
            orders_count.append(month_data['count'] if month_data else 0)
        
        context['months'] = '[' + ','.join(months) + ']'
        context['orders_by_month'] = orders_count
        
        # Добавляем статистику по типам грузов для диаграммы
        context['cargo_type_stats'] = json.dumps(get_cargo_statistics())
        
        return context

@login_required
def profile_view(request):
    """Профиль пользователя"""
    if hasattr(request.user, 'driver'):
        role = 'driver'
        orders = Order.objects.filter(driver=request.user.driver)
    elif hasattr(request.user, 'client'):
        role = 'client'
        orders = Order.objects.filter(client=request.user.client)
    elif request.user.is_superuser:
        role = 'admin'
        orders = Order.objects.all()
    else:
        role = None
        orders = Order.objects.none()

    context = {
        'role': role,
        'orders': orders[:10]  # Последние 10 заказов
    }
    return render(request, 'core/profile.html', context)

def about_view(request):
    """О компании"""
    return render(request, 'core/about.html')

def register_view(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('home')
    else:
        form = ClientRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})

class PublicVehicleListView(ListView):
    """Публичный список транспортных средств"""
    model = Vehicle
    template_name = 'core/public/vehicle_list.html'
    context_object_name = 'vehicles'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация
        body_type = self.request.GET.get('body_type')
        if body_type:
            queryset = queryset.filter(body_type__id=body_type)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['body_types'] = VehicleBodyType.objects.all()
        return context

class PublicDriverListView(ListView):
    """Публичный список водителей"""
    model = Driver
    template_name = 'core/public/driver_list.html'
    context_object_name = 'drivers'
    
    def get_queryset(self):
        return Driver.objects.select_related('user').order_by('-experience')

class PublicServiceListView(ListView):
    """Публичный список услуг"""
    model = Service
    template_name = 'core/public/service_list.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по цене
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        cargo_type = self.request.GET.get('cargo_type')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if cargo_type:
            queryset = queryset.filter(cargo_types__id=cargo_type)
            
        return queryset.distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cargo_types'] = CargoType.objects.all()
        return context

class PublicPromotionListView(ListView):
    """Публичный список акций и промокодов"""
    model = Promotion
    template_name = 'core/public/promotion_list.html'
    context_object_name = 'promotions'
    
    def get_queryset(self):
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )

class PublicCouponListView(ListView):
    """Публичный список купонов"""
    model = Coupon
    template_name = 'core/public/coupon_list.html'
    context_object_name = 'coupons'
    
    def get_queryset(self):
        now = timezone.now()
        return Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )

class NewsListView(ListView):
    """Список новостей"""
    model = News
    template_name = 'core/news_list.html'
    context_object_name = 'news'
    paginate_by = 10
    
    def get_queryset(self):
        return News.objects.filter(is_published=True).order_by('-created_at')

class NewsDetailView(DetailView):
    """Детальная страница новости"""
    model = News
    template_name = 'core/news_detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return News.objects.filter(is_published=True)

class NewsCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание новости"""
    model = News
    form_class = NewsForm
    template_name = 'core/news_form.html'
    success_url = reverse_lazy('news-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Новость успешно создана!')
        return super().form_valid(form)

class NewsUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование новости"""
    model = News
    form_class = NewsForm
    template_name = 'core/news_form.html'
    success_url = reverse_lazy('news-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Новость успешно обновлена!')
        return super().form_valid(form)

class FAQListView(ListView):
    """Список вопросов и ответов"""
    model = FAQ
    template_name = 'core/faq_list.html'
    context_object_name = 'faqs'
    paginate_by = 20

    def get_queryset(self):
        return FAQ.objects.filter(is_published=True)

class PrivacyPolicyView(TemplateView):
    """Политика конфиденциальности"""
    template_name = 'core/privacy_policy.html'

class JobListView(ListView):
    """Список вакансий"""
    model = Job
    template_name = 'core/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 10

    def get_queryset(self):
        return Job.objects.filter(is_active=True)

class ReviewListView(ListView):
    """Список отзывов"""
    model = Review
    template_name = 'core/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 10

    def get_queryset(self):
        return Review.objects.filter(is_published=True)

class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Создание отзыва"""
    model = Review
    template_name = 'core/review_form.html'
    fields = ['text', 'rating']
    success_url = reverse_lazy('review-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Спасибо за ваш отзыв!')
        return super().form_valid(form)

# Объединенный список акций и купонов
class PromotionCouponListView(ListView):
    """Список акций и купонов"""
    template_name = 'core/promotion_coupon_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        now = timezone.now()
        promotions = Promotion.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )
        coupons = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        )
        return {
            'promotions': promotions,
            'coupons': coupons
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем случайную шутку
        joke = get_random_joke()
        if not joke.get('error', True):
            if joke['type'] == 'twopart':
                context['joke_setup'] = joke['setup']
                context['joke_delivery'] = joke['delivery']
            else:
                context['joke'] = joke['joke']
        return context

def home(request):
    context = {
        'total_orders': Order.objects.count() if 'Order' in globals() else 0,
        'active_drivers': Driver.objects.filter(is_available=True).count() if 'Driver' in globals() else 0,
        'available_vehicles': Vehicle.objects.filter(is_available=True).count() if 'Vehicle' in globals() else 0,
    }
    return render(request, 'core/home.html', context)

class VehicleCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Создание транспортного средства"""
    model = Vehicle
    form_class = VehicleForm
    template_name = 'core/vehicle_form.html'
    success_url = reverse_lazy('vehicle-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Транспортное средство успешно добавлено!')
        return super().form_valid(form)

class VehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование транспортного средства"""
    model = Vehicle
    form_class = VehicleForm
    template_name = 'core/vehicle_form.html'
    success_url = reverse_lazy('vehicle-list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Транспортное средство успешно обновлено!')
        return super().form_valid(form)

@login_required
def driver_list(request):
    """Список водителей"""
    if not request.user.is_superuser:
        return redirect('home')
    
    # Получаем параметры фильтрации
    availability = request.GET.get('availability')
    min_experience = request.GET.get('min_experience')
    
    # Базовый QuerySet
    drivers = Driver.objects.all()
    
    # Применяем фильтры
    if availability in ['0', '1']:
        drivers = drivers.filter(is_available=bool(int(availability)))
    if min_experience:
        drivers = drivers.filter(experience__gte=int(min_experience))
    
    # Статистика
    all_drivers = Driver.objects.all()
    context = {
        'drivers': drivers,
        'avg_age': round(sum(driver.age() for driver in all_drivers) / max(len(all_drivers), 1), 1),
        'avg_experience': round(all_drivers.aggregate(Avg('experience'))['experience__avg'] or 0, 1),
        'available_count': all_drivers.filter(is_available=True).count()
    }
    
    return render(request, 'core/driver_list.html', context)

@login_required
def driver_create(request):
    """Создание водителя"""
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES)
        if form.is_valid():
            driver = form.save()
            messages.success(request, 'Водитель успешно добавлен!')
            return redirect('driver-list')
    else:
        form = DriverForm()
    
    return render(request, 'core/driver_form.html', {'form': form})

@login_required
def driver_update(request, pk):
    """Редактирование водителя"""
    if not request.user.is_superuser:
        return redirect('home')
    
    driver = get_object_or_404(Driver, pk=pk)
    
    if request.method == 'POST':
        form = DriverForm(request.POST, request.FILES, instance=driver)
        if form.is_valid():
            driver = form.save()
            messages.success(request, 'Данные водителя успешно обновлены!')
            return redirect('driver-list')
    else:
        form = DriverForm(instance=driver)
    
    return render(request, 'core/driver_form.html', {'form': form})

@login_required
def driver_delete(request, pk):
    """Удаление водителя"""
    if not request.user.is_superuser:
        return redirect('home')
    
    driver = get_object_or_404(Driver, pk=pk)
    
    if request.method == 'POST':
        driver.delete()
        messages.success(request, 'Водитель успешно удален!')
        return redirect('driver-list')
    
    return render(request, 'core/driver_confirm_delete.html', {'driver': driver})

def public_driver_list(request):
    """Публичный список водителей"""
    drivers = Driver.objects.select_related('user').order_by('-experience')
    return render(request, 'core/public/driver_list.html', {'drivers': drivers}) 