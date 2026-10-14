"""Журналирование изменяющих запросов авторизованных пользователей."""
from .audit import write_audit

POST_DESCRIPTIONS = {
    "accounts:register": "Регистрация обучающегося",
    "accounts:profile": "Изменение профиля",
    "accounts:application_new": "Подача заявки на договор",
    "contracts:application_decide": "Решение по заявке",
    "contracts:contract_add": "Создание договора",
    "contracts:payment_add": "Регистрация платежа",
    "contracts:file_add": "Загрузка файла договора",
    "pages:contacts": "Обращение через форму обратной связи",
}


class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._log(request)
        except Exception:
            pass
        return response

    def _log(self, request):
        if request.method != "POST":
            return
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return
        if request.path.startswith(("/static", "/media", "/admin/jsi18n")):
            return
        view_name = request.resolver_match.view_name if request.resolver_match else ""
        write_audit(
            user=user,
            action=f"{request.method} {request.path}",
            entity=view_name,
            description=POST_DESCRIPTIONS.get(view_name, "Изменение данных в сервисе"),
        )
