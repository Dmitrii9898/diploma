from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import AppUser


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"class": "form-control"}))


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(label="ФИО", max_length=160, widget=forms.TextInput(attrs={"class": "form-control"}))
    email = forms.EmailField(label="Эл. почта", widget=forms.EmailInput(attrs={"class": "form-control"}))
    phone = forms.CharField(label="Телефон", required=False, widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = AppUser
        fields = ("username", "full_name", "email", "phone")
        widgets = {"username": forms.TextInput(attrs={"class": "form-control"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("password1", "password2"):
            self.fields[name].widget.attrs["class"] = "form-control"


class ProfileForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ("full_name", "email", "phone", "student_code")
        labels = {
            "full_name": "ФИО",
            "email": "Эл. почта",
            "phone": "Телефон",
            "student_code": "Номер личного дела",
        }
        widgets = {name: forms.TextInput(attrs={"class": "form-control"}) for name in fields}
        widgets["email"] = forms.EmailInput(attrs={"class": "form-control"})
