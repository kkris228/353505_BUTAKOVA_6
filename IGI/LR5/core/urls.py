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
    path('orders/create/', views.OrderCreateView.as_view(), name='order-create'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    
    # Водители
    path('drivers/', views.driver_list, name='driver-list'),
    path('drivers/create/', views.driver_create, name='driver-create'),
    path('drivers/<int:pk>/update/', views.driver_update, name='driver-update'),
    path('drivers/<int:pk>/delete/', views.driver_delete, name='driver-delete'),
    
    # Транспорт
    path('vehicles/', views.VehicleListView.as_view(), name='vehicle-list'),
    path('vehicles/create/', views.VehicleCreateView.as_view(), name='vehicle-create'),
    path('vehicles/<int:pk>/update/', views.VehicleUpdateView.as_view(), name='vehicle-update'),
    
    # Статистика
    path('statistics/', views.StatisticsView.as_view(), name='statistics'),
    
    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page=reverse_lazy('home')
    ), name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Новости
    path('news/', views.NewsListView.as_view(), name='news-list'),
    path('news/create/', views.NewsCreateView.as_view(), name='news-create'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news-detail'),
    path('news/<int:pk>/update/', views.NewsUpdateView.as_view(), name='news-update'),
    
    # FAQ и политика
    path('faq/', views.FAQListView.as_view(), name='faq-list'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy-policy'),
    
    # Вакансии
    path('jobs/', views.JobListView.as_view(), name='job-list'),
    
    # Отзывы
    path('reviews/', views.ReviewListView.as_view(), name='review-list'),
    path('reviews/new/', views.ReviewCreateView.as_view(), name='review-create'),
    
    # Публичные URL
    path('public/vehicles/', views.PublicVehicleListView.as_view(), name='public-vehicle-list'),
    path('public/drivers/', views.public_driver_list, name='public-driver-list'),
    path('public/services/', views.PublicServiceListView.as_view(), name='public-service-list'),
    path('public/promotions-and-coupons/', views.PromotionCouponListView.as_view(), name='promotion-coupon-list'),
] 