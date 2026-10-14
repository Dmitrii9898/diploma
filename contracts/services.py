"""Правила договорного учёта: номер, график, одобрение заявки, задолженность."""
from datetime import date

from django.db import transaction
from django.utils import timezone

from .models import Contract, ContractStatus, Installment, Payer


def next_contract_number(year=None):
    """Номер вида Д-2025-0007. Последовательность считается внутри календарного года."""
    year = year or timezone.localdate().year
    prefix = f"Д-{year}-"
    last = (
        Contract.objects.filter(number__startswith=prefix)
        .order_by("-number")
        .values_list("number", flat=True)
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(last.rsplit("-", 1)[-1]) + 1
        except ValueError:
            seq = Contract.objects.filter(number__startswith=prefix).count() + 1
    return f"{prefix}{seq:04d}"


def build_installments(contract, first_due, second_due):
    """Делит годовую стоимость на два семестровых платежа."""
    first = contract.amount_rub // 2
    second = contract.amount_rub - first
    Installment.objects.bulk_create([
        Installment(contract=contract, due_on=first_due, amount_rub=first, title="Оплата 1 семестра"),
        Installment(contract=contract, due_on=second_due, amount_rub=second, title="Оплата 2 семестра"),
    ])


def ensure_payer(user):
    payer = Payer.objects.filter(user=user).first()
    if payer:
        return payer
    return Payer.objects.create(
        user=user,
        full_name=user.full_name or user.username,
        phone=user.phone,
        email=user.email,
    )


@transaction.atomic
def approve_application(application, specialist, starts_on, ends_on, first_due, second_due, note=""):
    """Одобряет заявку и создаёт договор со статусом «На подписании»."""
    if application.contract_id:
        return application.contract
    status = ContractStatus.objects.get(name="На подписании")
    payer = ensure_payer(application.user)
    contract = Contract.objects.create(
        number=next_contract_number(starts_on.year),
        program=application.program,
        payer=payer,
        student=application.user,
        status=status,
        starts_on=starts_on,
        ends_on=ends_on,
        amount_rub=application.program.tuition_rub,
        comment=note,
    )
    build_installments(contract, first_due, second_due)
    application.status = application.Status.APPROVED
    application.decision_note = note
    application.decided_at = timezone.now()
    application.decided_by = specialist
    application.contract = contract
    application.save()
    return contract


def mark_overdue(today=None):
    """Возвращает неоплаченные строки графика с истёкшим сроком."""
    today = today or date.today()
    return (
        Installment.objects.filter(is_paid=False, due_on__lt=today)
        .select_related("contract", "contract__student", "contract__program")
    )


def register_payment(contract, amount_rub, paid_on, method, purpose, installment=None):
    """Фиксирует платёж и закрывает строку графика, если сумма покрыта."""
    from .models import Payment

    payment = Payment.objects.create(
        contract=contract,
        installment=installment,
        amount_rub=amount_rub,
        paid_on=paid_on,
        method=method,
        purpose=purpose,
    )
    if installment is not None:
        covered = sum(installment.payments.values_list("amount_rub", flat=True))
        if covered >= installment.amount_rub:
            installment.is_paid = True
            installment.save(update_fields=["is_paid"])
    return payment
