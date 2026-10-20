from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
from apps.users.views import LoginView

urlpatterns = [

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
    # products
        path(
            "api/v1/products/",
            include("apps.products.urls"),
        ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        
        document_root=settings.MEDIA_ROOT,
    )