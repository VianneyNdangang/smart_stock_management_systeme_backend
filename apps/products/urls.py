from django.urls import path
from . import views


urlpatterns = [
    # Products
    path(
        "",
        views.ProductsListCreateView.as_view(),
        name="product-list-create",
    ),
    path(
        "<uuid:id>/",
        views.ProductsDetailView.as_view(),
        name="product-detail",
    ),

    # Attributes
    path(
        "attributes/",
        views.AttributeListCreateView.as_view(),
        name="attribute-list-create",
    ),

    # Attribute values
    path(
        "attribute-values/",
        views.AttributeValueListCreateView.as_view(),
        name="attribute-value-list-create",
    ),

    # Variants
    path(
        "<uuid:product_id>/variants/",
        views.VariantListCreateView.as_view(),
        name="product-variant-list-create",
    ),
]