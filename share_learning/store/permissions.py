from urllib import request
from rest_framework import permissions

from .models import Post, PostComment


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthenticatedAndHasPermitted(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.groups.filter(name='modirator'):
            return True
        return False


class IsSuperOrHasPostPermissionsOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return bool((request.user and request.user.groups.filter(name='post_modirator')) or request.user.is_superuser)


class IsSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user.is_superuser)


class IsSuperOrHasCustomerPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_superuser or request.user.groups.filter(name='customer_modirator'))


class IsPostOwner(permissions.BasePermission):
    def has_permission(self, request, view):

        post_id = view.kwargs.get('pk')


        if post_id is None:
            if request.method in permissions.SAFE_METHODS:
                return True
            return False

        post_user_id = (Post.objects.filter(
            id=post_id)).values()[0]['user_id']

        user_id = request.user.id

        if user_id == post_user_id:
            if request.method in permissions.SAFE_METHODS or request.method == 'PATCH':
                return True
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return False


class IsCommentOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        comment_id = view.kwargs.get('pk')

        if comment_id is None:
            if request.method in permissions.SAFE_METHODS:
                return True
            return False

        comment_user_id = (PostComment.objects.filter(
            id=comment_id)).values()[0]['user_id']


        user_id = request.user.id
        
        if user_id == comment_user_id:
            if request.method in permissions.SAFE_METHODS or request.method == 'PATCH':
                return True
            return False

        if request.method in permissions.SAFE_METHODS:
            return True

        return False

        
