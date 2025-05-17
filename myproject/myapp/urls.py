# myproject/myapp/urls.py

from . import views
from django.contrib.auth import views as auth_views
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'profiles', views.UserProfileViewSet, basename='userprofile')
router.register(r'communities', views.CommunityViewSet, basename='community')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'events', views.EventViewSet, basename='event')
router.register(r'attendances', views.AttendanceViewSet, basename='attendance')

# Webpage URLs
urlpatterns = [
    path('', views.home, name='home'),
    path('events/', views.EventListView.as_view(), name='event_list'),
    path('events/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('events/create/', views.EventCreateView.as_view(), name='event_create'),
    path('events/<int:pk>/edit/', views.EventUpdateView.as_view(), name='event_update'),
    path('events/<int:pk>/attend/', views.attend_event, name='attend_event'),

    # Profile related URLs - Reordered for specificity
    path('profile/edit/', views.edit_profile, name='edit_profile'), # Specific before general
    path('profile/points-history/', views.points_history_view, name='points_history'), # Specific before general
    path('profile/', views.user_profile, name='user_profile'), # For current user, no username in URL
    path('profile/<str:username>/', views.user_profile, name='view_profile'), # For viewing other users' profiles

    path('dashboard/', views.dashboard_page, name='dashboard'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='myapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('signup/', views.signup, name='signup'),

    # --- URLs ใหม่สำหรับระบบแต้มและของรางวัล ---
    path('rewards/', views.rewards_store_view, name='rewards_store'),
    path('rewards/redeem/<int:reward_id>/', views.redeem_reward_view, name='redeem_reward'),
    # path('profile/points-history/', views.points_history_view, name='points_history'), # ย้ายไปอยู่กับกลุ่ม profile แล้ว

    # -----------------------------------------

    # API URLs
    path('api/', include(router.urls)),
]
