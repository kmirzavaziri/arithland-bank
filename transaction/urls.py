from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('', views.dashboard_view, name='dashboard'),

    path('teams/', views.teams_view, name='teams'),
    path('teams/get_balance_by_number', views.teams_get_balance_by_number_view, name='teams__get_balance_by_number'),

    path('transactions/', views.transactions_view, name='transactions'),

    path('manage/', views.manage_view, name='manage'),
]
