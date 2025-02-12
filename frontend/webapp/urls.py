"""
URL configuration for frontend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views  # Ensure 'views' is imported

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_to_backend, name="login"),
    path("logout/", views.logout_from_backend, name="logout"),
    path("admin/healthcheck/", views.home, name="healthcheck"),
    path("admin/users/", views.list_users, name="list_users"),  # Ensure this line is correct
    path("admin/usermod/", views.usermod, name="usermod"),
    path("create-user/", views.create_user, name="create_user"),
    path("create-admin/", views.create_admin, name="create_admin"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("passes-cost/", views.passes_cost_view, name="passes_cost"),
    path("api/getTransactions/<tollOpID>/<tagOpID>/<date_from>/<date_to>/", views.api_passes_cost, name="api_passes_cost"),
    path("api/tollStationPasses/<tollStationID>/<date_from>/<date_to>/", views.toll_station_passes, name="toll_station_passes"),
    path("pay-transactions/", views.pay_transactions, name="pay_transactions"),
]