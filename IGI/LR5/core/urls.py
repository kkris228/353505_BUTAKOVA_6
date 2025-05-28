from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about_view, name='about'),
    path('profile/', views.profile_view, name='profile'),
    
    # Заказы
    path('orders/', views.OrderListView.as_view(), name='order-list'),
    path('orders/new/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Водители и транспорт
    path('drivers/', views.DriverListView.as_view(), name='driver-list'),
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    
    # Статистика
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page=reverse_lazy('home')
    ), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Публичные URL
    path('public/vehicles/', views.PublicVehicleListView.as_view(), name='public-vehicle-list'),
    path('public/drivers/', views.PublicDriverListView.as_view(), name='public-driver-list'),
    path('public/services/', views.PublicServiceListView.as_view(), name='public-service-list'),
    path('public/promotions/', views.PublicPromotionListView.as_view(), name='public-promotion-list'),
    path('public/coupons/', views.PublicCouponListView.as_view(), name='public-coupon-list'),
] 