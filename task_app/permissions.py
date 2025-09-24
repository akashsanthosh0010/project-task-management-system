from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superadmin())

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin())

class IsAssignedUser(permissions.BasePermission):
    """
    Allows access only to the user assigned to the task (for view/update).
    SuperAdmin and Admins may have other permissions in the views.
    """
    def has_object_permission(self, request, view, obj):
        # obj is Task
        return bool(request.user and request.user.is_authenticated and obj.assigned_to == request.user)
