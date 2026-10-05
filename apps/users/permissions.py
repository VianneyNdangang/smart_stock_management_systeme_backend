from rest_framework.permissions import BasePermission

from apps.users.constants import Form


class IsAdmin(BasePermission):

    message = (
        "Seuls les administrateurs peuvent gérer "
        "les utilisateurs."
    )

    def has_permission(self, request, view):

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == Form.ROLE_ADMIN
        )

class IsAdminOrManager(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        return (
            user.is_authenticated
            and user.role in ["ADMIN", "MANAGER"]
        )