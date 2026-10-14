"""Проверка основных сценариев без браузера."""
import os
import sys

import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

from contracts.models import Contract


def main():
    client = Client()
    public_paths = [
        "/", "/about/", "/programs/", "/programs/bi/", "/pricing/", "/howto/",
        "/news/", "/documents/", "/faq/", "/glossary/", "/help/", "/contacts/",
        "/accounts/login/", "/accounts/register/",
    ]
    for path in public_paths:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)

    news = client.get("/news/")
    assert b"news" in news.content or "Новости".encode() in news.content

    assert client.login(username="student", password="Student#2025")
    for path in [
        "/accounts/cabinet/",
        "/accounts/cabinet/applications/",
        "/accounts/cabinet/contracts/",
        "/accounts/cabinet/payments/",
        "/accounts/cabinet/documents/",
        "/accounts/cabinet/profile/",
    ]:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)
    denied = client.get("/office/")
    assert denied.status_code == 403
    client.logout()

    assert client.login(username="specialist", password="Specialist#2025")
    for path in ["/office/", "/office/applications/", "/office/contracts/", "/office/payments/", "/office/payers/", "/office/reports/"]:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)
    xlsx = client.get("/office/reports/?format=xlsx")
    docx = client.get("/office/reports/?format=docx")
    assert xlsx.status_code == 200 and xlsx["Content-Type"].startswith("application/vnd.openxmlformats")
    assert docx.status_code == 200
    assert client.get("/office/manage/").status_code == 403
    client.logout()

    assert client.login(username="admin", password="Admin#2025")
    for path in [
        "/office/manage/",
        "/office/manage/users/",
        "/office/manage/programs/",
        "/office/manage/news/",
        "/office/manage/feedback/",
        "/office/manage/audit/",
    ]:
        response = client.get(path)
        assert response.status_code == 200, (path, response.status_code)

    assert Contract.objects.filter(number="Д-2025-0001").exists()
    assert get_user_model().objects.filter(username="student").exists()
    print("smoke ok", len(public_paths), "public pages")


if __name__ == "__main__":
    main()
