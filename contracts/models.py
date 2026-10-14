"""Предметная область: программы, плательщики, договоры, графики и платежи."""
from django.conf import settings
from django.db import models
from django.urls import reverse


class Institute(models.Model):
    """Структурное подразделение, реализующее образовательную программу."""

    name = models.CharField("Наименование", max_length=160, unique=True)
    short_name = models.CharField("Краткое наименование", max_length=40)
    code = models.CharField("Код", max_length=16, unique=True)

    class Meta:
        db_table = "institute"
        verbose_name = "Институт"
        verbose_name_plural = "Институты"
        ordering = ["name"]

    def __str__(self):
        return self.short_name


class StudyForm(models.Model):
    name = models.CharField("Наименование", max_length=40, unique=True)

    class Meta:
        db_table = "study_form"
        verbose_name = "Форма обучения"
        verbose_name_plural = "Формы обучения"
        ordering = ["name"]

    def __str__(self):
        return self.name


class EducationLevel(models.Model):
    name = models.CharField("Наименование", max_length=40, unique=True)

    class Meta:
        db_table = "education_level"
        verbose_name = "Уровень образования"
        verbose_name_plural = "Уровни образования"
        ordering = ["id"]

    def __str__(self):
        return self.name


class EducationProgram(models.Model):
    """Образовательная программа и годовая стоимость обучения."""

    institute = models.ForeignKey(Institute, on_delete=models.PROTECT, related_name="programs", verbose_name="Институт")
    level = models.ForeignKey(EducationLevel, on_delete=models.PROTECT, related_name="programs", verbose_name="Уровень")
    study_form = models.ForeignKey(StudyForm, on_delete=models.PROTECT, related_name="programs", verbose_name="Форма")
    code = models.CharField("Код направления", max_length=20)
    name = models.CharField("Наименование", max_length=200)
    slug = models.SlugField("Ссылка", max_length=80, unique=True)
    tuition_rub = models.PositiveIntegerField("Стоимость за год, руб.")
    duration_years = models.DecimalField("Срок, лет", max_digits=3, decimal_places=1)
    description = models.TextField("Описание")
    is_active = models.BooleanField("Приём открыт", default=True)

    class Meta:
        db_table = "education_program"
        verbose_name = "Образовательная программа"
        verbose_name_plural = "Образовательные программы"
        ordering = ["code", "name"]

    def __str__(self):
        return f"{self.code} {self.name}"

    def get_absolute_url(self):
        return reverse("pages:program_detail", args=[self.slug])


class Payer(models.Model):
    """Плательщик по договору: сам обучающийся или иное лицо."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payer_profiles",
        verbose_name="Учётная запись",
    )
    full_name = models.CharField("ФИО", max_length=160)
    phone = models.CharField("Телефон", max_length=30, blank=True)
    email = models.EmailField("Эл. почта", blank=True)
    passport = models.CharField("Паспорт", max_length=40, blank=True)
    address = models.CharField("Адрес", max_length=240, blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        db_table = "payer"
        verbose_name = "Плательщик"
        verbose_name_plural = "Плательщики"
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name


class ContractStatus(models.Model):
    name = models.CharField("Наименование", max_length=40, unique=True)
    is_final = models.BooleanField("Конечный статус", default=False)

    class Meta:
        db_table = "contract_status"
        verbose_name = "Статус договора"
        verbose_name_plural = "Статусы договоров"
        ordering = ["id"]

    def __str__(self):
        return self.name


class Contract(models.Model):
    """Договор об оказании платных образовательных услуг."""

    number = models.CharField("Номер", max_length=32, unique=True)
    program = models.ForeignKey(EducationProgram, on_delete=models.PROTECT, related_name="contracts", verbose_name="Программа")
    payer = models.ForeignKey(Payer, on_delete=models.PROTECT, related_name="contracts", verbose_name="Плательщик")
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="contracts",
        verbose_name="Обучающийся",
    )
    status = models.ForeignKey(ContractStatus, on_delete=models.PROTECT, related_name="contracts", verbose_name="Статус")
    signed_on = models.DateField("Дата подписания", null=True, blank=True)
    starts_on = models.DateField("Начало обучения")
    ends_on = models.DateField("Окончание обучения")
    amount_rub = models.PositiveIntegerField("Сумма за год, руб.")
    scan = models.FileField("Скан договора", upload_to="contracts/", blank=True)
    comment = models.TextField("Комментарий", blank=True)
    created_at = models.DateTimeField("Создан", auto_now_add=True)

    class Meta:
        db_table = "contract"
        verbose_name = "Договор"
        verbose_name_plural = "Договоры"
        ordering = ["-created_at"]

    def __str__(self):
        return self.number

    @property
    def paid_rub(self):
        return sum(self.payments.values_list("amount_rub", flat=True))

    @property
    def debt_rub(self):
        return max(self.amount_rub - self.paid_rub, 0)


class Installment(models.Model):
    """Строка графика оплаты."""

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="installments", verbose_name="Договор")
    due_on = models.DateField("Срок оплаты")
    amount_rub = models.PositiveIntegerField("Сумма, руб.")
    title = models.CharField("Назначение", max_length=80)
    is_paid = models.BooleanField("Оплачен", default=False)

    class Meta:
        db_table = "installment"
        verbose_name = "Платёж по графику"
        verbose_name_plural = "График платежей"
        ordering = ["due_on"]

    def __str__(self):
        return f"{self.contract.number}: {self.title}"


class Payment(models.Model):
    """Фактически поступивший платёж."""

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="payments", verbose_name="Договор")
    installment = models.ForeignKey(
        Installment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Строка графика",
    )
    amount_rub = models.PositiveIntegerField("Сумма, руб.")
    paid_on = models.DateField("Дата оплаты")
    method = models.CharField("Способ", max_length=40, default="Безналичный")
    purpose = models.CharField("Назначение", max_length=160)
    created_at = models.DateTimeField("Зарегистрирован", auto_now_add=True)

    class Meta:
        db_table = "payment"
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ["-paid_on"]

    def __str__(self):
        return f"{self.amount_rub} руб. по {self.contract.number}"


class Application(models.Model):
    """Заявка обучающегося на заключение договора."""

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        REVIEW = "review", "На рассмотрении"
        APPROVED = "approved", "Одобрена"
        REJECTED = "rejected", "Отклонена"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications", verbose_name="Заявитель")
    program = models.ForeignKey(EducationProgram, on_delete=models.PROTECT, related_name="applications", verbose_name="Программа")
    status = models.CharField("Статус", max_length=16, choices=Status.choices, default=Status.NEW)
    comment = models.TextField("Комментарий заявителя", blank=True)
    decision_note = models.TextField("Решение отдела", blank=True)
    passport_scan = models.FileField("Скан документа", upload_to="applications/", blank=True)
    created_at = models.DateTimeField("Подана", auto_now_add=True)
    decided_at = models.DateTimeField("Решение принято", null=True, blank=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="decided_applications",
        verbose_name="Кто решил",
    )
    contract = models.OneToOneField(
        Contract,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_application",
        verbose_name="Созданный договор",
    )

    class Meta:
        db_table = "application"
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка #{self.pk} — {self.user}"


class ContractFile(models.Model):
    """Дополнительный файл по договору (доп. соглашение, квитанция, скан)."""

    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name="files", verbose_name="Договор")
    title = models.CharField("Наименование", max_length=160)
    file = models.FileField("Файл", upload_to="contract_files/")
    uploaded_at = models.DateTimeField("Загружен", auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_files",
        verbose_name="Кто загрузил",
    )

    class Meta:
        db_table = "contract_file"
        verbose_name = "Файл договора"
        verbose_name_plural = "Файлы договоров"
        ordering = ["-uploaded_at"]

    def __str__(self):
        return self.title


class AuditLog(models.Model):
    """Журнал действий пользователей."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_entries",
        verbose_name="Пользователь",
    )
    action = models.CharField("Действие", max_length=200)
    entity = models.CharField("Объект", max_length=120, blank=True)
    description = models.CharField("Описание", max_length=240, blank=True)
    created_at = models.DateTimeField("Когда", auto_now_add=True)

    class Meta:
        db_table = "audit_log"
        verbose_name = "Запись журнала"
        verbose_name_plural = "Журнал действий"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.created_at:%d.%m.%Y %H:%M} {self.action}"
