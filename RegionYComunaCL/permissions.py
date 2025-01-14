from rest_framework.permissions import BasePermission


class IsStaffOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # Permite el acceso solo si el usuario es staff o superuser
        return request.user and (request.user.is_staff or request.user.is_superuser)