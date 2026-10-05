from rest_framework.permissions import BasePermission


class HasPermission(BasePermission):

    message = "Vous n'avez pas les permissions nécessaires."

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        permissions = getattr(
            view,
            "required_permission",
            None
        )

        if not permissions:
            return False

        if isinstance(permissions, str):
            permissions = [permissions]

        return all(
            request.user.has_perm(permission)
            for permission in permissions
        )