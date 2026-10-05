from django.urls import path
from . import views

urlpatterns = [
    path( '', views.CategoriesListCreateView.as_view(), name='category-list-create'),
    path( '<uuid:id>/', views.CategoriesDetailView.as_view(), name='category-detail'),
]