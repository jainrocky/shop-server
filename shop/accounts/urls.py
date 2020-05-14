from django.urls import path
from .views import (
    all_users,
    all_histories,
    list_users,
    register,
    login,
    update_profile,
    get_profile,
)

urlpatterns = [
    path('users/profile/', get_profile, name='get_profile'),
    path('users/all/', all_users, name='all_users'),
    path('histories/all/', all_histories, name='all_histories'),
    path('users/list/', list_users, name='list_users'),
    path('users/register/', register, name='register_users'),
    path('users/login/', login, name='login_users'),
    path('users/update/profile/',
         update_profile, name='update_profiles'),
]
