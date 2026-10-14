from django.urls import path

from . import views

app_name = "contracts"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("applications/", views.application_queue, name="applications"),
    path("applications/<int:pk>/", views.application_decide, name="application_decide"),
    path("contracts/", views.contract_list, name="contracts"),
    path("contracts/new/", views.contract_add, name="contract_add"),
    path("contracts/<int:pk>/", views.contract_detail, name="contract_detail"),
    path("payments/", views.payment_list, name="payments"),
    path("payers/", views.payer_list, name="payers"),
    path("reports/", views.reports, name="reports"),
    path("manage/", views.manage_home, name="manage_home"),
    path("manage/users/", views.manage_users, name="manage_users"),
    path("manage/programs/", views.manage_programs, name="manage_programs"),
    path("manage/news/", views.manage_news, name="manage_news"),
    path("manage/feedback/", views.manage_feedback, name="manage_feedback"),
    path("manage/audit/", views.manage_audit, name="manage_audit"),
]
