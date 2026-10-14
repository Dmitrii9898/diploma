from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ("name", "email", "subject", "message")
        labels = {
            "name": "Имя",
            "email": "Эл. почта",
            "subject": "Тема",
            "message": "Сообщение",
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "subject": forms.TextInput(attrs={"class": "form-control"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
