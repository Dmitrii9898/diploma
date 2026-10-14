"""Пользователи и роли веб-сервиса «Договор.Онлайн»."""
from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_ADMIN = "Администратор"
ROLE_SPECIALIST = "Специалист"
ROLE_STUDENT = "Обучающийся"


class Role(models.Model):
    """Уровень доступа: администратор, специалист договорного отдела, обучающийся."""

    name = models.CharField("Наименование", max_length=40, unique=True)
    description = models.CharField("Описание", max_length=240, blank=True)

    class Meta:
        db_table = "role"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        ordering = ["id"]

    def __str__(self):
        return self.name


class AppUser(AbstractUser):
    """Учётная запись. Студенческий идентификатор хранится отдельно от логина."""

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="users",
        verbose_name="Роль",
    )
    full_name = models.CharField("ФИО", max_length=160, blank=True)
    phone = models.CharField("Телефон", max_length=30, blank=True)
    student_code = models.CharField("Номер личного дела", max_length=32, blank=True)

    class Meta:
        db_table = "app_user"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.full_name or self.username

    @property
    def role_name(self):
        return self.role.name if self.role_id else ""

    def has_role(self, *names):
        return self.role_name in names

    @property
    def is_admin_role(self):
        return self.has_role(ROLE_ADMIN) or self.is_superuser

    @property
    def is_specialist_role(self):
        return self.has_role(ROLE_SPECIALIST)

    @property
    def is_student_role(self):
        return self.has_role(ROLE_STUDENT)
