from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard_view, name="dashboard"),
    path("teams/", views.teams_view, name="teams"),
    path("transactions/", views.transactions_view, name="transactions"),
    path(
        "api/admin/get-user-details/<int:user_id>",
        views.get_user_details_api_view,
        name="api-admin-get_user_details",
    ),
    path(
        "api/teams/get_balance_by_number",
        views.teams_get_balance_by_number_api_view,
        name="api-teams-get_balance_by_number",
    ),
    path(
        "api/user/set_competition",
        views.set_user_competition_api_view,
        name="api-user-set_competition",
    ),
]
