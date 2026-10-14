from django import forms

from .models import Application, Contract, ContractFile, EducationProgram, Payment


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ("program", "comment", "passport_scan")
        labels = {
            "program": "Образовательная программа",
            "comment": "Комментарий",
            "passport_scan": "Скан документа (необязательно)",
        }
        widgets = {
            "program": forms.Select(attrs={"class": "form-select"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "passport_scan": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["program"].queryset = EducationProgram.objects.filter(is_active=True)


class DecisionForm(forms.Form):
    note = forms.CharField(
        label="Комментарий решения",
        required=False,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}),
    )
    starts_on = forms.DateField(label="Начало обучения", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    ends_on = forms.DateField(label="Окончание обучения", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    first_due = forms.DateField(label="Срок 1-го платежа", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    second_due = forms.DateField(label="Срок 2-го платежа", widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))


class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ("program", "payer", "student", "status", "signed_on", "starts_on", "ends_on", "amount_rub", "scan", "comment")
        widgets = {
            "program": forms.Select(attrs={"class": "form-select"}),
            "payer": forms.Select(attrs={"class": "form-select"}),
            "student": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "signed_on": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "starts_on": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "ends_on": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "amount_rub": forms.NumberInput(attrs={"class": "form-control"}),
            "scan": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ("contract", "installment", "amount_rub", "paid_on", "method", "purpose")
        widgets = {
            "contract": forms.Select(attrs={"class": "form-select"}),
            "installment": forms.Select(attrs={"class": "form-select"}),
            "amount_rub": forms.NumberInput(attrs={"class": "form-control"}),
            "paid_on": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "method": forms.TextInput(attrs={"class": "form-control"}),
            "purpose": forms.TextInput(attrs={"class": "form-control"}),
        }


class ContractFileForm(forms.ModelForm):
    class Meta:
        model = ContractFile
        fields = ("title", "file")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
