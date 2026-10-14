"""Демонстрационные справочники, договоры и учётные записи."""
from datetime import date
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import ROLE_ADMIN, ROLE_SPECIALIST, ROLE_STUDENT, AppUser, Role
from contracts.models import (
    Application,
    Contract,
    ContractStatus,
    EducationLevel,
    EducationProgram,
    Institute,
    Payer,
    Payment,
    StudyForm,
)
from contracts.services import build_installments
from pages.models import Feedback, News


class Command(BaseCommand):
    help = "Заполняет базу демонстрационными данными «Договор.Онлайн»."

    def handle(self, *args, **options):
        roles = {
            ROLE_ADMIN: "Ведёт пользователей, стоимость и журнал",
            ROLE_SPECIALIST: "Рассматривает заявки и регистрирует оплату",
            ROLE_STUDENT: "Подаёт заявку и видит свои договоры",
        }
        role_objects = {}
        for name, description in roles.items():
            role_objects[name], _ = Role.objects.get_or_create(
                name=name, defaults={"description": description}
            )

        admin = self._user("admin", "Admin#2025", ROLE_ADMIN, "Соколова Ирина Петровна", staff=True)
        specialist = self._user("specialist", "Specialist#2025", ROLE_SPECIALIST, "Орлова Мария Сергеевна", staff=True)
        student = self._user("student", "Student#2025", ROLE_STUDENT, "Курбатов Дмитрий Евгеньевич", code="70199902")
        second = self._user("ivanov", "Ivanov#2025", ROLE_STUDENT, "Иванов Алексей Павлович", code="70191011")

        economics = self._institute("Институт экономики и бизнеса", "ИЭБ", "IEB")
        law = self._institute("Юридический институт", "ЮИ", "LAW")
        full_time = self._form("Очная")
        part_time = self._form("Очно-заочная")
        bachelor = self._level("Бакалавриат")

        programs = [
            self._program(economics, bachelor, full_time, "38.03.05", "Бизнес-информатика", "bi", 186000, "Подготовка специалистов, которые связывают экономику предприятия и информационные системы."),
            self._program(economics, bachelor, full_time, "38.03.01", "Экономика", "econ", 174000, "Учёт, анализ и планирование финансовых показателей организации."),
            self._program(economics, bachelor, part_time, "38.03.02", "Менеджмент", "mgmt", 142000, "Управление подразделениями и проектами, в том числе в сфере услуг."),
            self._program(law, bachelor, full_time, "40.03.01", "Юриспруденция", "law", 198000, "Правовое сопровождение договоров и претензионной работы."),
            self._program(economics, bachelor, full_time, "09.03.03", "Прикладная информатика", "pi", 192000, "Проектирование прикладных информационных систем для организаций."),
            self._program(economics, bachelor, part_time, "42.03.01", "Реклама и связи с общественностью", "adv", 156000, "Коммуникации организации и продвижение образовательных программ."),
        ]

        status_names = ["Проект", "На подписании", "Действует", "Приостановлен", "Расторгнут", "Исполнен"]
        statuses = {}
        for name in status_names:
            statuses[name], _ = ContractStatus.objects.get_or_create(
                name=name, defaults={"is_final": name in {"Расторгнут", "Исполнен"}}
            )

        payer_student = self._payer(student, "4510 123456", "г. Москва")
        payer_second = self._payer(second, "4511 654321", "г. Москва")

        active = self._contract(
            "Д-2025-0001", programs[0], payer_student, student, statuses["Действует"],
            date(2025, 9, 1), date(2029, 8, 31), date(2025, 8, 28),
        )
        waiting = self._contract(
            "Д-2025-0002", programs[3], payer_second, second, statuses["На подписании"],
            date(2025, 9, 1), date(2029, 8, 31), None,
        )
        if not active.installments.exists():
            build_installments(active, date(2025, 9, 1), date(2026, 2, 1))
        if not waiting.installments.exists():
            build_installments(waiting, date(2025, 9, 10), date(2026, 2, 10))
        first = active.installments.order_by("due_on").first()
        Payment.objects.get_or_create(
            contract=active,
            purpose="Оплата 1 семестра",
            defaults={
                "installment": first,
                "amount_rub": first.amount_rub,
                "paid_on": date(2025, 8, 29),
                "method": "Безналичный",
            },
        )
        first.is_paid = True
        first.save(update_fields=["is_paid"])

        if not active.scan:
            active.scan.save(
                "dogovor-d-2025-0001.txt",
                ContentFile("Учебный файл скана договора Д-2025-0001.\n".encode("utf-8")),
                save=True,
            )

        Application.objects.get_or_create(
            user=second,
            program=programs[1],
            status=Application.Status.REVIEW,
            defaults={"comment": "Прошу подготовить договор на экономику, очная форма."},
        )
        Application.objects.get_or_create(
            user=student,
            program=programs[0],
            status=Application.Status.APPROVED,
            defaults={"comment": "Заявка, по которой создан договор Д-2025-0001.", "contract": active, "decided_by": specialist},
        )

        news_items = [
            ("График оплаты на 2025/2026 учебный год", "grafik-2025", "Два платежа: сентябрь и февраль.", "Договорной отдел публикует ориентир сроков. Точные даты стоят в карточке договора."),
            ("Как приложить скан паспорта к заявке", "skan-zayavki", "Файл не обязателен, но ускоряет проверку.", "В форме заявки есть поле для файла. Специалист открывает его из карточки заявки."),
            ("Выгрузка реестра для бухгалтерии", "reestr-excel", "Реестр скачивается в Excel и Word.", "В разделе отчётов специалист получает файл со статусами и суммами."),
        ]
        for title, slug, summary, body in news_items:
            News.objects.get_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "body": body,
                    "published_at": timezone.now(),
                    "is_published": True,
                },
            )
        Feedback.objects.get_or_create(
            email="parent@example.com",
            subject="Вопрос по графику",
            defaults={
                "name": "Петрова Анна",
                "message": "Можно ли перенести февральский платёж на март?",
            },
        )
        self.stdout.write(self.style.SUCCESS("Демонстрационные данные загружены."))
        self.stdout.write("admin / Admin#2025")
        self.stdout.write("specialist / Specialist#2025")
        self.stdout.write("student / Student#2025")

    def _user(self, username, password, role_name, full_name, code="", staff=False):
        user, created = AppUser.objects.get_or_create(
            username=username,
            defaults={
                "full_name": full_name,
                "email": f"{username}@educontract.example",
                "role": Role.objects.get(name=role_name),
                "student_code": code,
                "is_staff": staff,
                "phone": "+7 900 000-00-00",
            },
        )
        if created:
            user.set_password(password)
            user.save()
        return user

    def _institute(self, name, short_name, code):
        obj, _ = Institute.objects.get_or_create(code=code, defaults={"name": name, "short_name": short_name})
        return obj

    def _form(self, name):
        obj, _ = StudyForm.objects.get_or_create(name=name)
        return obj

    def _level(self, name):
        obj, _ = EducationLevel.objects.get_or_create(name=name)
        return obj

    def _program(self, institute, level, form, code, name, slug, tuition, description):
        obj, _ = EducationProgram.objects.get_or_create(
            slug=slug,
            defaults={
                "institute": institute,
                "level": level,
                "study_form": form,
                "code": code,
                "name": name,
                "tuition_rub": tuition,
                "duration_years": Decimal("4.0"),
                "description": description,
                "is_active": True,
            },
        )
        return obj

    def _payer(self, user, passport, address):
        obj, _ = Payer.objects.get_or_create(
            user=user,
            defaults={
                "full_name": user.full_name,
                "phone": user.phone,
                "email": user.email,
                "passport": passport,
                "address": address,
            },
        )
        return obj

    def _contract(self, number, program, payer, student, status, starts, ends, signed):
        obj, _ = Contract.objects.get_or_create(
            number=number,
            defaults={
                "program": program,
                "payer": payer,
                "student": student,
                "status": status,
                "starts_on": starts,
                "ends_on": ends,
                "signed_on": signed,
                "amount_rub": program.tuition_rub,
            },
        )
        return obj
