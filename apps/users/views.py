from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenViewBase
from .models import User
from django.contrib.auth.models import Group, Permission
from .serializers import UserCreateSerializer, LoginSerializer, UserAdminUpdateSerializer, UserReadSerializer, UserUpdateSerializer, ChangePasswordSerializer, GroupCreateSerializer, PermissionSummarySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Q
from permissions import HasPermission, PermissionCodes

class UsersListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.filter(deleted_at__isnull=True)

    def get_permissions(self):
        if self.request.method == "GET":
            self.required_permission = PermissionCodes.VIEW_USERS

        elif self.request.method == "POST":
            self.required_permission = PermissionCodes.CREATE_USERS

        return [HasPermission()]
    
    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserReadSerializer

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_admin=Count(
                "id",
                filter=Q(role="ADMIN")
            ),
            total_category_manager=Count(
                "id",
                filter=Q(role="CATEGORY MANAGER")
            ),
            total_foot_worker=Count(
                "id",
                filter=Q(role="FOOT WORKER")
            ),
            total_active=Count(
                "id",
                filter=Q(is_active=True)
            ),
            total_inactive=Count(
                "id",
                filter=Q(is_active=False)
            ),
        )

    filterset_fields = [
        "warehouse",
        "role",
        "is_active",
        "created_at",
    ]
    search_fields = [
        "username",
        "first_name",
        "last_name"
    ]
    ordering_fields = [
        "created_at",
        "username",
        "first_name"
    ]


class UserDetailView(generics.RetrieveUpdateAPIView):

    queryset = User.objects.filter(deleted_at__isnull=True)
    lookup_field = "id"

    def get_permissions(self):
        permission_map = {
            "GET": PermissionCodes.VIEW_USERS,
            "PUT": PermissionCodes.UPDATE_USERS,
            "PATCH": PermissionCodes.UPDATE_USERS,
        }

        self.required_permission = permission_map.get(
            self.request.method
        )

        return [HasPermission()]
    
    def get_serializer_class(self):
        # Consultation
        if self.request.method == "GET":
            return UserReadSerializer

        # Modification
        if self.request.method in ["PUT", "PATCH"]:
            if self.request.user.role == "ADMIN":
                return UserAdminUpdateSerializer

            return UserUpdateSerializer
        return UserReadSerializer
    

class CurrentUserView(generics.RetrieveAPIView):
    """
    Retourne les informations de l'utilisateur actuellement connecté.
    """
    serializer_class = UserReadSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    """
    Permet à l'utilisateur connecté de modifier son mot de passe.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)

        request.user.set_password(
            serializer.validated_data["new_password"]
        )

        request.user.save(
            update_fields=["password"]
        )

        return Response(
            {
                "detail": "Mot de passe modifié avec succès."
            },
            status=status.HTTP_200_OK,
        )

class GroupListView(generics.ListCreateAPIView):
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupCreateSerializer
    pagination_class = None
    def get_permissions(self):
        if self.request.method == "GET":
            self.required_permission = PermissionCodes.VIEW_GROUPS

        elif self.request.method == "POST":
            self.required_permission = PermissionCodes.CREATE_GROUPS

        return [HasPermission()]

    
class GroupDetailView(generics.RetrieveUpdateAPIView):
    queryset = Group.objects.all()
    lookup_field = "id"
    def get_permissions(self):
        permission_map = {
            "GET": PermissionCodes.VIEW_GROUPS,
            "PUT": PermissionCodes.UPDATE_GROUPS,
            "PATCH": PermissionCodes.UPDATE_GROUPS,
        }

        self.required_permission = permission_map.get(
            self.request.method
        )

        return [HasPermission()]
    serializer_class = GroupCreateSerializer

class PermissionListView(generics.ListAPIView):
    queryset = Permission.objects.all().order_by("-id")
    serializer_class = PermissionSummarySerializer
    # permission_classes = [HasPermission]
    # required_permission = [PermissionCodes.VIEW_PERMISSIONS]
    pagination_class = None

class LoginView(TokenViewBase):
    serializer_class = LoginSerializer