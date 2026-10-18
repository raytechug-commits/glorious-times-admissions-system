
from django.contrib import admin
from .models import AdmissionApplication


@admin.register(AdmissionApplication)
class AdmissionApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "application_number",
        "pupil_first_name",
        "pupil_last_name",
        "class_applying_for",
        "parent_full_name",
        "status",
        "submitted_at",
    )

    list_filter = (
        "status",
        "class_applying_for",
        "submitted_at",
    )

    search_fields = (
        "application_number",
        "pupil_first_name",
        "pupil_last_name",
        "parent_full_name",
        "parent_email",
        "parent_phone",
    )

    readonly_fields = (
        "application_number",
        "submitted_at",
    )

    ordering = ("-submitted_at",)
