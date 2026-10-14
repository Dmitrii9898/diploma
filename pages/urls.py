from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("programs/", views.program_list, name="program_list"),
    path("programs/<slug:slug>/", views.program_detail, name="program_detail"),
    path("pricing/", views.pricing, name="pricing"),
    path("howto/", views.howto, name="howto"),
    path("news/", views.news_list, name="news_list"),
    path("news/<slug:slug>/", views.news_detail, name="news_detail"),
    path("documents/", views.documents, name="documents"),
    path("faq/", views.faq, name="faq"),
    path("glossary/", views.glossary, name="glossary"),
    path("help/", views.help_page, name="help"),
    path("contacts/", views.contacts, name="contacts"),
]
