"""Рабочее место договорного отдела и панель администратора."""
from datetime import date

from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.mixins import admin_required, office_required
from accounts.models import AppUser, Role
from pages.models import Feedback, News

from .exports import contracts_to_docx, contracts_to_xlsx
from .forms import ContractFileForm, ContractForm, DecisionForm, PaymentForm
from .models import (
    Application,
    AuditLog,
    Contract,
    EducationProgram,
    Installment,
    Payer,
    Payment,
)
from .services import approve_application, mark_overdue, register_payment


def _contract_qs():
    return Contract.objects.select_related("student", "program", "status", "payer")


@office_required
def dashboard(request):
    request.breadcrumbs = [("Договорной отдел", None)]
    today = date.today()
    active = _contract_qs().filter(status__name="Действует")
    totals = active.aggregate(amount=Sum("amount_rub"))
    paid = Payment.objects.filter(contract__status__name="Действует").aggregate(amount=Sum("amount_rub"))
    by_program = (
        EducationProgram.objects.annotate(total=Count("contracts"))
        .filter(total__gt=0)
        .order_by("-total")
    )
    return render(request, "office/dashboard.html", {
        "active_count": active.count(),
        "amount": totals["amount"] or 0,
        "paid": paid["amount"] or 0,
        "new_applications": Application.objects.filter(status=Application.Status.REVIEW).count(),
        "overdue": mark_overdue(today)[:8],
        "by_program": by_program,
    })


@office_required
def application_queue(request):
    request.breadcrumbs = [("Договорной отдел", "/office/"), ("Заявки", None)]
    items = Application.objects.select_related("user", "program").all()
    return render(request, "office/applications.html", {"items": items})


@office_required
def application_decide(request, pk):
    item = get_object_or_404(Application.objects.select_related("user", "program"), pk=pk)
    request.breadcrumbs = [
        ("Договорной отдел", "/office/"),
        ("Заявки", "/office/applications/"),
        (f"Заявка #{item.pk}", None),
    ]
    form = DecisionForm(request.POST or None, initial={
        "starts_on": date(date.today().year, 9, 1),
        "ends_on": date(date.today().year + 4, 8, 31),
        "first_due": date(date.today().year, 9, 1),
        "second_due": date(date.today().year + 1, 2, 1),
    })
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "reject":
            item.status = Application.Status.REJECTED
            item.decision_note = request.POST.get("note", "")
            item.decided_at = timezone.now()
            item.decided_by = request.user
            item.save()
            messages.success(request, "Заявка отклонена.")
            return redirect("contracts:applications")
        if action == "approve" and form.is_valid():
            approve_application(
                item,
                request.user,
                form.cleaned_data["starts_on"],
                form.cleaned_data["ends_on"],
                form.cleaned_data["first_due"],
                form.cleaned_data["second_due"],
                form.cleaned_data["note"],
            )
            messages.success(request, "Заявка одобрена, договор создан.")
            return redirect("contracts:contracts")
    return render(request, "office/application_decide.html", {"item": item, "form": form})


@office_required
def contract_list(request):
    request.breadcrumbs = [("Договорной отдел", "/office/"), ("Реестр договоров", None)]
    return render(request, "office/contracts.html", {"items": _contract_qs()})


@office_required
def contract_detail(request, pk):
    item = get_object_or_404(_contract_qs(), pk=pk)
    request.breadcrumbs = [
        ("Договорной отдел", "/office/"),
        ("Реестр договоров", "/office/contracts/"),
        (item.number, None),
    ]
    file_form = ContractFileForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and "upload" in request.POST and file_form.is_valid():
        saved = file_form.save(commit=False)
        saved.contract = item
        saved.uploaded_by = request.user
        saved.save()
        messages.success(request, "Файл загружен.")
        return redirect("contracts:contract_detail", pk=item.pk)
    return render(request, "office/contract_detail.html", {
        "item": item,
        "installments": item.installments.all(),
        "payments": item.payments.all(),
        "files": item.files.all(),
        "file_form": file_form,
    })


@office_required
def contract_add(request):
    request.breadcrumbs = [
        ("Договорной отдел", "/office/"),
        ("Реестр договоров", "/office/contracts/"),
        ("Новый договор", None),
    ]
    form = ContractForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        contract = form.save(commit=False)
        if not contract.number:
            from .services import next_contract_number
            contract.number = next_contract_number()
        contract.save()
        messages.success(request, f"Договор {contract.number} сохранён.")
        return redirect("contracts:contract_detail", pk=contract.pk)
    return render(request, "office/contract_form.html", {"form": form})


@office_required
def payment_list(request):
    request.breadcrumbs = [("Договорной отдел", "/office/"), ("Платежи", None)]
    form = PaymentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        register_payment(
            data["contract"], data["amount_rub"], data["paid_on"],
            data["method"], data["purpose"], data["installment"],
        )
        messages.success(request, "Платёж зарегистрирован.")
        return redirect("contracts:payments")
    items = Payment.objects.select_related("contract", "contract__student")[:50]
    return render(request, "office/payments.html", {"items": items, "form": form})


@office_required
def payer_list(request):
    request.breadcrumbs = [("Договорной отдел", "/office/"), ("Плательщики", None)]
    return render(request, "office/payers.html", {"items": Payer.objects.all()})


@office_required
def reports(request):
    request.breadcrumbs = [("Договорной отдел", "/office/"), ("Отчёты", None)]
    items = _contract_qs()
    if request.GET.get("format") == "xlsx":
        return contracts_to_xlsx(items)
    if request.GET.get("format") == "docx":
        return contracts_to_docx(items)
    overdue = mark_overdue()
    return render(request, "office/reports.html", {"count": items.count(), "overdue": overdue})


@admin_required
def manage_home(request):
    request.breadcrumbs = [("Администрирование", None)]
    return render(request, "manage/home.html", {
        "users": AppUser.objects.count(),
        "programs": EducationProgram.objects.count(),
        "news": News.objects.count(),
        "feedback": Feedback.objects.filter(is_processed=False).count(),
        "audit": AuditLog.objects.count(),
    })


@admin_required
def manage_users(request):
    request.breadcrumbs = [("Администрирование", "/office/manage/"), ("Пользователи", None)]
    if request.method == "POST":
        user = get_object_or_404(AppUser, pk=request.POST.get("user_id"))
        role = get_object_or_404(Role, pk=request.POST.get("role_id"))
        user.role = role
        user.is_staff = role.name == "Администратор"
        user.save(update_fields=["role", "is_staff"])
        messages.success(request, f"Роль пользователя {user} изменена.")
        return redirect("contracts:manage_users")
    return render(request, "manage/users.html", {
        "items": AppUser.objects.select_related("role"),
        "roles": Role.objects.all(),
    })


@admin_required
def manage_programs(request):
    request.breadcrumbs = [("Администрирование", "/office/manage/"), ("Программы", None)]
    if request.method == "POST":
        program = get_object_or_404(EducationProgram, pk=request.POST.get("program_id"))
        raw = request.POST.get("tuition_rub", "").strip()
        if raw.isdigit():
            program.tuition_rub = int(raw)
            program.save(update_fields=["tuition_rub"])
            messages.success(request, f"Стоимость программы «{program.name}» обновлена.")
        return redirect("contracts:manage_programs")
    return render(request, "manage/programs.html", {"items": EducationProgram.objects.select_related("institute", "study_form")})


@admin_required
def manage_news(request):
    request.breadcrumbs = [("Администрирование", "/office/manage/"), ("Новости", None)]
    if request.method == "POST":
        item = get_object_or_404(News, pk=request.POST.get("news_id"))
        item.is_published = not item.is_published
        item.save(update_fields=["is_published"])
        messages.success(request, "Статус публикации изменён.")
        return redirect("contracts:manage_news")
    return render(request, "manage/news.html", {"items": News.objects.all()})


@admin_required
def manage_feedback(request):
    request.breadcrumbs = [("Администрирование", "/office/manage/"), ("Обращения", None)]
    if request.method == "POST":
        item = get_object_or_404(Feedback, pk=request.POST.get("feedback_id"))
        item.is_processed = True
        item.save(update_fields=["is_processed"])
        messages.success(request, "Обращение отмечено как обработанное.")
        return redirect("contracts:manage_feedback")
    return render(request, "manage/feedback.html", {"items": Feedback.objects.all()})


@admin_required
def manage_audit(request):
    request.breadcrumbs = [("Администрирование", "/office/manage/"), ("Журнал действий", None)]
    return render(request, "manage/audit.html", {"items": AuditLog.objects.select_related("user")[:100]})
