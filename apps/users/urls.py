
from django.urls import path
from . import views

urlpatterns = [
    path( '', views.UsersListCreateView.as_view(), name='users-list-create'),
    path( '<uuid:id>/', views.UserDetailView.as_view(), name='user-detail'),
    path( 'change-password/', views.ChangePasswordView.as_view(), name='user-change-password'),
    path( 'me/', views.CurrentUserView.as_view(), name='user-detail-profile'),
    path( 'permissions-groups/', views.GroupListView.as_view(), name='groups-list'),
     path( 'permissions-groups/<id>', views.GroupDetailView.as_view(), name='groups-list-detail'),
    path( 'permissions/', views.PermissionListView.as_view(), name='permissions-list')
]