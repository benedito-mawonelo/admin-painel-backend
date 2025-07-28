# users/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomUserViewSet, RoleViewSet, UserActivityViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'roles', RoleViewSet, basename='roles')
router.register(r'activities/(?P<user_id>\d+)', UserActivityViewSet, basename='activities')

urlpatterns = [
    path('', include(router.urls)),
]