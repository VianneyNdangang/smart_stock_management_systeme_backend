
from django.urls import path
from . import views

urlpatterns = [
    path( '', views.WarehousesListCreateView.as_view(), name='warehouse-list-create'),
    path( '<uuid:id>/', views.WarehouseDetailView.as_view(), name='warehouse-detail')
]