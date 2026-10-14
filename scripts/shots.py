"""Скриншоты работающего сервиса для отчёта."""
import os

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765"
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "figures"))
os.makedirs(OUT, exist_ok=True)


def shot(page, url, name):
    page.goto(BASE + url, wait_until="networkidle")
    page.screenshot(path=os.path.join(OUT, name), full_page=True)
    print("saved", name)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        public = browser.new_context(viewport={"width": 1366, "height": 900})
        page = public.new_page()
        for url, name in [
            ("/", "shot_home.png"),
            ("/programs/", "shot_programs.png"),
            ("/contacts/", "shot_contacts.png"),
            ("/help/", "shot_help.png"),
        ]:
            shot(page, url, name)
        mobile = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
        mp = mobile.new_page()
        shot(mp, "/", "shot_mobile.png")

        student = browser.new_context(viewport={"width": 1366, "height": 900})
        sp = student.new_page()
        shot(sp, "/accounts/login/", "shot_login.png")
        sp.fill("input[name=username]", "student")
        sp.fill("input[name=password]", "Student#2025")
        sp.click("button[type=submit]")
        sp.wait_for_load_state("networkidle")
        shot(sp, "/accounts/cabinet/", "shot_cabinet.png")
        shot(sp, "/accounts/cabinet/contracts/", "shot_my_contracts.png")

        office = browser.new_context(viewport={"width": 1366, "height": 900})
        op = office.new_page()
        shot(op, "/accounts/login/", "shot_login_office.png")
        op.fill("input[name=username]", "specialist")
        op.fill("input[name=password]", "Specialist#2025")
        op.click("button[type=submit]")
        op.wait_for_load_state("networkidle")
        for url, name in [
            ("/office/", "shot_office.png"),
            ("/office/contracts/", "shot_registry.png"),
            ("/office/reports/", "shot_reports.png"),
        ]:
            shot(op, url, name)

        admin = browser.new_context(viewport={"width": 1366, "height": 900})
        ap = admin.new_page()
        ap.goto(BASE + "/accounts/login/", wait_until="networkidle")
        ap.fill("input[name=username]", "admin")
        ap.fill("input[name=password]", "Admin#2025")
        ap.click("button[type=submit]")
        ap.wait_for_load_state("networkidle")
        shot(ap, "/office/manage/", "shot_admin.png")
        shot(ap, "/office/manage/audit/", "shot_audit.png")
        browser.close()


if __name__ == "__main__":
    main()
