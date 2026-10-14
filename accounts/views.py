from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render

from contracts.forms import ApplicationForm
from contracts.models import Application, Contract, ContractFile, Installment, Payment

from .forms import LoginForm, ProfileForm, RegisterForm
from .models import ROLE_STUDENT, Role


class UserLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get(self, request, *args, **kwargs):
        request.breadcrumbs = [("Вход", None)]
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        request.breadcrumbs = [("Вход", None)]
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        user = self.request.user
        if user.is_admin_role:
            return "/office/manage/"
        if user.is_specialist_role:
            return "/office/"
        return "/accounts/cabinet/"


class UserLogoutView(LogoutView):
    next_page = "pages:home"


def register(request):
    request.breadcrumbs = [("Регистрация", None)]
    if request.user.is_authenticated:
        return redirect("accounts:cabinet")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.full_name = form.cleaned_data["full_name"]
        user.phone = form.cleaned_data["phone"]
        user.role, _created = Role.objects.get_or_create(
            name=ROLE_STUDENT,
            defaults={"description": "Подаёт заявку и видит свои договоры"},
        )
        user.save()
        login(request, user)
        messages.success(request, "Учётная запись создана. Можно подать заявку на договор.")
        return redirect("accounts:cabinet")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def cabinet(request):
    request.breadcrumbs = [("Личный кабинет", None)]
    contracts = Contract.objects.filter(student=request.user).select_related("status", "program")
    applications = Application.objects.filter(user=request.user).select_related("program")
    next_payment = (
        Installment.objects.filter(contract__student=request.user, is_paid=False)
        .select_related("contract")
        .order_by("due_on")
        .first()
    )
    return render(request, "accounts/cabinet.html", {
        "contracts": contracts,
        "applications": applications,
        "next_payment": next_payment,
    })


@login_required
def application_list(request):
    request.breadcrumbs = [("Личный кабинет", "/accounts/cabinet/"), ("Мои заявки", None)]
    items = Application.objects.filter(user=request.user).select_related("program")
    return render(request, "accounts/applications.html", {"items": items})


@login_required
def application_new(request):
    request.breadcrumbs = [
        ("Личный кабинет", "/accounts/cabinet/"),
        ("Мои заявки", "/accounts/cabinet/applications/"),
        ("Новая заявка", None),
    ]
    form = ApplicationForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.user = request.user
        item.status = Application.Status.REVIEW
        item.save()
        messages.success(request, "Заявка отправлена в договорной отдел.")
        return redirect("accounts:applications")
    return render(request, "accounts/application_new.html", {"form": form})


@login_required
def contract_list(request):
    request.breadcrumbs = [("Личный кабинет", "/accounts/cabinet/"), ("Мои договоры", None)]
    items = Contract.objects.filter(student=request.user).select_related("status", "program", "payer")
    return render(request, "accounts/contracts.html", {"items": items})


@login_required
def contract_detail(request, pk):
    item = get_object_or_404(
        Contract.objects.select_related("status", "program", "payer"),
        pk=pk,
        student=request.user,
    )
    request.breadcrumbs = [
        ("Личный кабинет", "/accounts/cabinet/"),
        ("Мои договоры", "/accounts/cabinet/contracts/"),
        (item.number, None),
    ]
    return render(request, "accounts/contract_detail.html", {
        "item": item,
        "installments": item.installments.all(),
        "payments": item.payments.all(),
        "files": item.files.all(),
    })


@login_required
def payment_list(request):
    request.breadcrumbs = [("Личный кабинет", "/accounts/cabinet/"), ("Мои платежи", None)]
    items = Payment.objects.filter(contract__student=request.user).select_related("contract")
    schedule = Installment.objects.filter(contract__student=request.user).select_related("contract")
    return render(request, "accounts/payments.html", {"items": items, "schedule": schedule})


@login_required
def document_list(request):
    request.breadcrumbs = [("Личный кабинет", "/accounts/cabinet/"), ("Мои документы", None)]
    files = ContractFile.objects.filter(contract__student=request.user).select_related("contract")
    scans = Contract.objects.filter(student=request.user).exclude(scan="")
    return render(request, "accounts/documents.html", {"files": files, "scans": scans})


@login_required
def profile(request):
    request.breadcrumbs = [("Личный кабинет", "/accounts/cabinet/"), ("Профиль", None)]
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль сохранён.")
        return redirect("accounts:profile")
    return render(request, "accounts/profile.html", {"form": form})
