from django.contrib import admin

from .models import Feedback, News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "published_at", "is_published")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_published",)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "created_at", "is_processed")
    list_filter = ("is_processed",)
