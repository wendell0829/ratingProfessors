from django.urls import path

from . import views

urlpatterns = [
    path('session/login/', views.login, name='login'),
    path('user/register/', views.register, name='register'),
    path('session/', views.session, name='session'),
    path('session/logout/', views.logout, name='logout'),
    path('modules/list/', views.modules_list, name='modules_list'),
    path('ratings/average/', views.ratings_avg, name='ratings_avg'),
    path('ratings/view/', views.ratings_view, name='ratings_view'),
    path('ratings/rate/', views.ratings_rate, name='ratings_rate'),
]