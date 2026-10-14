from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.UserLoginView.as_view(), name="login"),
    path("logout/", views.UserLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("cabinet/", views.cabinet, name="cabinet"),
    path("cabinet/applications/", views.application_list, name="applications"),
    path("cabinet/applications/new/", views.application_new, name="application_new"),
    path("cabinet/contracts/", views.contract_list, name="contracts"),
    path("cabinet/contracts/<int:pk>/", views.contract_detail, name="contract_detail"),
    path("cabinet/payments/", views.payment_list, name="payments"),
    path("cabinet/documents/", views.document_list, name="documents"),
    path("cabinet/profile/", views.profile, name="profile"),
]
