from django.contrib import admin

from .models import (
    Application,
    AuditLog,
    Contract,
    ContractFile,
    ContractStatus,
    EducationLevel,
    EducationProgram,
    Installment,
    Institute,
    Payer,
    Payment,
    StudyForm,
)


admin.site.register(Institute)
admin.site.register(StudyForm)
admin.site.register(EducationLevel)
admin.site.register(ContractStatus)
admin.site.register(Payer)
admin.site.register(Installment)
admin.site.register(Payment)
admin.site.register(ContractFile)
admin.site.register(AuditLog)


@admin.register(EducationProgram)
class EducationProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "study_form", "tuition_rub", "is_active")
    list_filter = ("study_form", "level", "is_active")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ("number", "student", "program", "status", "amount_rub", "starts_on")
    list_filter = ("status", "program")
    search_fields = ("number", "student__full_name", "student__username")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "program", "status", "created_at")
    list_filter = ("status",)
