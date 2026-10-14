"""Публичные страницы сервиса. Доступны без авторизации."""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from contracts.models import EducationProgram, Institute

from .forms import FeedbackForm
from .models import News


def home(request):
    request.breadcrumbs = []
    programs = EducationProgram.objects.filter(is_active=True).select_related("study_form")[:4]
    news = News.objects.filter(is_published=True)[:3]
    return render(request, "pages/home.html", {"programs": programs, "news": news})


def about(request):
    request.breadcrumbs = [("О сервисе", None)]
    return render(request, "pages/about.html")


def program_list(request):
    request.breadcrumbs = [("Программы", None)]
    items = EducationProgram.objects.filter(is_active=True).select_related("institute", "level", "study_form")
    institute = request.GET.get("institute")
    if institute:
        items = items.filter(institute__code=institute)
    return render(request, "pages/programs.html", {
        "items": items,
        "institutes": Institute.objects.all(),
        "current": institute or "",
    })


def program_detail(request, slug):
    item = get_object_or_404(
        EducationProgram.objects.select_related("institute", "level", "study_form"),
        slug=slug,
        is_active=True,
    )
    request.breadcrumbs = [("Программы", "/programs/"), (item.name, None)]
    return render(request, "pages/program_detail.html", {"item": item})


def pricing(request):
    request.breadcrumbs = [("Стоимость", None)]
    items = EducationProgram.objects.filter(is_active=True).select_related("study_form", "level")
    return render(request, "pages/pricing.html", {"items": items})


def howto(request):
    request.breadcrumbs = [("Как заключить договор", None)]
    return render(request, "pages/howto.html")


def news_list(request):
    request.breadcrumbs = [("Новости", None)]
    return render(request, "pages/news_list.html", {"items": News.objects.filter(is_published=True)})


def news_detail(request, slug):
    item = get_object_or_404(News, slug=slug, is_published=True)
    request.breadcrumbs = [("Новости", "/news/"), (item.title, None)]
    return render(request, "pages/news_detail.html", {"item": item})


def documents(request):
    request.breadcrumbs = [("Документы", None)]
    return render(request, "pages/documents.html")


def faq(request):
    request.breadcrumbs = [("Вопросы и ответы", None)]
    return render(request, "pages/faq.html")


def glossary(request):
    request.breadcrumbs = [("Глоссарий", None)]
    return render(request, "pages/glossary.html")


def help_page(request):
    request.breadcrumbs = [("Справка", None)]
    return render(request, "pages/help.html")


def contacts(request):
    request.breadcrumbs = [("Контакты", None)]
    form = FeedbackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Сообщение отправлено. Договорной отдел ответит на указанную почту.")
        return redirect("pages:contacts")
    return render(request, "pages/contacts.html", {"form": form})
