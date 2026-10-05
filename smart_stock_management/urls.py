from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from apps.users.views import LoginView

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentication
    path(
        "api/v1/auth/",
        LoginView.as_view(),
        name="token_obtain_pair",
    ),
    # path(
    #     "api/v1/auth/token/refresh/",
    #     TokenRefreshView.as_view(),
    #     name="token_refresh",
    # ),

    # Users
    path(
        "api/v1/users/",
        include("apps.users.urls"),
    ),

    # Warehouses
        path(
            "api/v1/warehouses/",
            include("apps.warehouses.urls"),
        ),

     # Categories
            path(
                "api/v1/categories/",
                include("apps.categories.urls"),
            ),
]