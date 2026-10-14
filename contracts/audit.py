"""Запись в журнал действий."""
from .models import AuditLog


def write_audit(user, action, entity="", description=""):
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action[:200],
        entity=entity[:120],
        description=description[:240],
    )
