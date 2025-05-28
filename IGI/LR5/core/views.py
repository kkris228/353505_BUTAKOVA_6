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
from datetime import date
from django import forms

from .models import (
    Organization, Driver, Vehicle, Client, Order, 
    Promotion, CargoType, Service, VehicleBodyType,
    Coupon, News, FAQ, Job, Review
)
from .forms import ClientRegistrationForm
from .services import NewsService, JokeService

class HomeView(ListView):
    """Главная страница"""
    model = Order
    template_name = 'core/home.html'
    context_object_name = 'orders'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Статистика
        context['total_orders'] = Order.objects.count()
        context['active_drivers'] = Driver.objects.filter(is_available=True).count()
        context['available_vehicles'] = Vehicle.objects.filter(is_available=True).count()
        
        # Публичная информация
        context['vehicles'] = Vehicle.objects.filter(is_available=True).order_by('-created_at')[:6]  # Последние 6 доступных транспортных средств
        context['drivers'] = Driver.objects.filter(is_available=True).order_by('-created_at')[:6]  # Последние 6 доступных водителей
        context['services'] = Service.objects.filter(is_active=True).order_by('-created_at')[:6]  # Последние 6 активных услуг
        
        # Акции и скидки
        context['promotions'] = Promotion.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        ).order_by('-valid_until')[:3]  # 3 активных промокода, сортировка по сроку действия
        
        context['coupons'] = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=now,
            valid_until__gte=now
        ).order_by('-valid_until')[:3]  # 3 активных купона, сортировка по сроку действия
        
        context['news'] = News.objects.all()[:5]  # Get latest 5 news articles
        
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

class StatisticsView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Статистика заказов"""
    model = Order
    template_name = 'core/statistics.html'
    context_object_name = 'orders'

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
        context['active_orders'] = orders.filter(status='IN_PROGRESS').count()
        
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
        
        # Статистика по водителям
        driver_stats = (
            Order.objects.values(
                'driver__user__first_name',
                'driver__user__last_name'
            )
            .filter(driver__isnull=False)  # Исключаем заказы без водителей
            .annotate(
                order_count=Count('id'),
                total_revenue=Sum('price'),
                avg_rating=Avg('rating')
            )
            .order_by('-order_count')[:10]  # Топ-10 водителей
        )
        
        # Преобразуем рейтинг в проценты и добавляем в контекст
        for stat in driver_stats:
            stat['rating'] = (stat['avg_rating'] or 0) * 20  # Преобразуем рейтинг 1-5 в проценты
        context['driver_stats'] = driver_stats
        
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
        monthly_revenue = []
        
        for month in range(1, 13):
            month_data = next((item for item in months_data if item['month'] == month), None)
            months.append(f'"{month_names[month - 1]}"')  # Добавляем кавычки для JSON
            orders_count.append(month_data['count'] if month_data else 0)
            monthly_revenue.append(round(month_data['revenue'] if month_data and month_data['revenue'] else 0, 2))
        
        context['months'] = '[' + ','.join(months) + ']'  # Формируем JSON-массив
        context['orders_by_month'] = orders_count
        context['revenue_by_month'] = monthly_revenue
        
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
        return Driver.objects.filter(is_available=True)

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
    ordering = ['-published_at']

class NewsDetailView(DetailView):
    """Детальная страница новости"""
    model = News
    template_name = 'core/news_detail.html'
    context_object_name = 'news'

    def get_queryset(self):
        return News.objects.filter(is_published=True)

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
        context['joke'] = JokeService.get_random_joke()
        return context

def home(request):
    context = {
        'total_orders': Order.objects.count() if 'Order' in globals() else 0,
        'active_drivers': Driver.objects.filter(is_active=True).count() if 'Driver' in globals() else 0,
        'available_vehicles': Vehicle.objects.filter(is_available=True).count() if 'Vehicle' in globals() else 0,
    }
    return render(request, 'core/home.html', context) 