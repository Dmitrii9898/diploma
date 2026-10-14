"""Проверки доступа по ролям."""
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import ROLE_ADMIN, ROLE_SPECIALIST


def office_required(view):
    """Договорной отдел: специалист и администратор."""

    @login_required
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_admin_role or user.is_specialist_role or user.has_role(ROLE_ADMIN, ROLE_SPECIALIST):
            return view(request, *args, **kwargs)
        raise PermissionDenied("Раздел доступен сотрудникам договорного отдела.")

    return wrapper


def admin_required(view):
    """Страницы, доступные только администратору."""

    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_admin_role:
            return view(request, *args, **kwargs)
        raise PermissionDenied("Раздел доступен только администратору.")

    return wrapper
