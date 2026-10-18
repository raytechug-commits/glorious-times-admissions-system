import logging
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from .models import AdmissionApplication
logger = logging.getLogger(__name__)


def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")

    applications = AdmissionApplication.objects.all()
    context = {
        "total_applications": applications.count(),
        "pending_applications": applications.filter(status="pending").count(),
        "reviewing_applications": applications.filter(status="reviewing").count(),
        "accepted_applications": applications.filter(status="accepted").count(),
        "recent_applications": applications.order_by("-submitted_at")[:10],
    }
    return render(request, "admissions/dashboard.html", context)


def _application_form(request, public=False):
    template = "admissions/add_application.html"
    today = timezone.localdate().isoformat()

    if request.method != "POST":
        return render(request, template, {
            "today": today,
            "public_application": public,
        })

    if request.POST.get("declaration_accepted") != "on":
        messages.error(request, "Please accept the declaration before submitting.")
        return render(request, template, {
            "today": today,
            "form_data": request.POST,
            "public_application": public,
        })

    required_fields = [
        "pupil_first_name", "pupil_last_name", "date_of_birth",
        "class_applying_for", "parent_full_name", "parent_phone",
        "residential_address", "declaration_name", "declaration_date",
    ]
    missing = [
        field for field in required_fields
        if not request.POST.get(field, "").strip()
    ]
    if missing:
        messages.error(request, "Please complete all required fields.")
        return render(request, template, {
            "today": today,
            "form_data": request.POST,
            "public_application": public,
        })

    try:
        application = AdmissionApplication(
            pupil_first_name=request.POST["pupil_first_name"].strip(),
            pupil_middle_name=request.POST.get("pupil_middle_name", "").strip(),
            pupil_last_name=request.POST["pupil_last_name"].strip(),
            date_of_birth=request.POST["date_of_birth"],
            gender=request.POST.get("gender", ""),
            class_applying_for=request.POST["class_applying_for"],
            previous_school=request.POST.get("previous_school", "").strip(),
            medical_information=request.POST.get("medical_information", "").strip(),
            parent_full_name=request.POST["parent_full_name"].strip(),
            parent_email=request.POST.get("parent_email", "").strip(),
            parent_phone=request.POST["parent_phone"].strip(),
            parent_relationship=request.POST.get("parent_relationship", "").strip(),
            father_full_name=request.POST.get("father_full_name", "").strip(),
            father_relationship=request.POST.get("father_relationship", "").strip(),
            father_phone=request.POST.get("father_phone", "").strip(),
            father_email=request.POST.get("father_email", "").strip(),
            father_occupation=request.POST.get("father_occupation", "").strip(),
            mother_full_name=request.POST.get("mother_full_name", "").strip(),
            mother_relationship=request.POST.get("mother_relationship", "").strip(),
            mother_phone=request.POST.get("mother_phone", "").strip(),
            mother_email=request.POST.get("mother_email", "").strip(),
            mother_occupation=request.POST.get("mother_occupation", "").strip(),
            residential_address=request.POST["residential_address"].strip(),
            additional_information=request.POST.get("additional_information", "").strip(),
            declaration_name=request.POST["declaration_name"].strip(),
            declaration_date=request.POST["declaration_date"],
            declaration_accepted=True,
        )

        with transaction.atomic():
            year = timezone.localdate().year
            prefix = f"APP{year}"
            last_reference = (
                AdmissionApplication.objects
                .filter(application_reference__startswith=prefix)
                .order_by("-application_reference")
                .values_list("application_reference", flat=True)
                .first()
            )
            next_number = (
                int(last_reference[-4:]) + 1 if last_reference else 1
            )
            application.application_reference = f"{prefix}{next_number:04d}"
            application.full_clean()
            application.save()

    except (ValidationError, ValueError, TypeError, IntegrityError):
        messages.error(
            request,
            "The application could not be saved. Please check the details and try again.",
        )
        return render(request, template, {
            "today": today,
            "form_data": request.POST,
            "public_application": public,
        })
    # Notify the parent contacts after the application has been saved.
    email_addresses = [
        application.parent_email,
        application.father_email,
        application.mother_email,
    ]

    recipients = list(dict.fromkeys(
        address.strip()
        for address in email_addresses
        if address and address.strip()
    ))

    if recipients:
        subject = (
            f"Application Received - "
            f"{application.application_reference}"
        )

        email_message = (
            f"Dear Parent/Guardian,\n\n"
            f"We have received the application for "
            f"{application.pupil_first_name} "
            f"{application.pupil_last_name}.\n\n"
            f"Application Reference: "
            f"{application.application_reference}\n"
            f"Class Applied For: {application.class_applying_for}\n\n"
            f"Please keep this reference for future communication "
            f"with Glorious Times Standards Nursery and Primary School.\n\n"
            f"This is an application reference, not an official "
            f"admission number. An official admission number will "
            f"be issued if the application is accepted.\n\n"
            f"Thank you.\n"
            f"Glorious Times Standards Nursery and Primary School\n"
            f"IN GOD WE TRUST"
        )

        try:
            send_mail(
                subject,
                email_message,
                None,
                recipients,
                fail_silently=False,
            )
        except Exception:
            logger.exception(
                "Application notification failed for reference %s",
                application.application_reference,
            )

    if public:
        return redirect(
            "admissions:confirmation",
            reference=application.application_reference,
        )

    messages.success(
        request,
        f"Application saved. Reference: {application.application_reference}",
    )
    return redirect("admissions:dashboard")


@login_required
def add_application(request):
    return _application_form(request, public=False)


def public_apply(request):
    return _application_form(request, public=True)


def application_confirmation(request, reference):
    application = get_object_or_404(
        AdmissionApplication,
        application_reference=reference,
    )
    return render(request, "admissions/confirmation.html", {
        "application": application,
    })
@login_required
def review_application(request, application_id):
    application = get_object_or_404(
        AdmissionApplication,
        pk=application_id,
    )
    return render(
        request,
        "admissions/review_application.html",
        {"application": application},
    )
@login_required
def update_application_status(request, application_id):
    if request.method != "POST":
        return redirect(
            "admissions:review_application",
            application_id=application_id,
        )
    application = get_object_or_404(
        AdmissionApplication,
        pk=application_id,
    )
    action = request.POST.get("action", "").strip()
    if action == "reviewing":
        application.status = "reviewing"
        application.rejection_reason = ""
        application.save(update_fields=["status", "rejection_reason"])
        messages.success(request, "Application marked as under review.")
    elif action == "accepted":
        from django.db.models import Q
        with transaction.atomic():
            application = AdmissionApplication.objects.select_for_update().get(
                pk=application_id
            )
            if not application.admission_number:
                year = timezone.localdate().year
                prefix = f"GT{year}-"
                existing_numbers = (
                    AdmissionApplication.objects
                    .filter(admission_number__startswith=prefix)
                    .values_list("admission_number", flat=True)
                )
                highest = 0
                for number in existing_numbers:
                    try:
                        highest = max(highest, int(number.rsplit("-", 1)[1]))
                    except (ValueError, IndexError):
                        continue
                application.admission_number = f"{prefix}{highest + 1:04d}"
            application.status = "accepted"
            application.rejection_reason = ""
            application.save(
                update_fields=[
                    "status",
                    "admission_number",
                    "rejection_reason",
                ]
            )
        messages.success(
            request,
            f"Application approved. Admission number: {application.admission_number}",
        )
    elif action == "rejected":
        reason = request.POST.get("rejection_reason", "").strip()
        if not reason:
            messages.error(request, "Please provide a reason for rejection.")
            return redirect(
                "admissions:review_application",
                application_id=application_id,
            )
        application.status = "rejected"
        application.rejection_reason = reason
        application.save(update_fields=["status", "rejection_reason"])
        messages.success(request, "Application rejected and reason saved.")
    else:
        messages.error(request, "Unknown application action.")
    return redirect(
        "admissions:review_application",
        application_id=application_id,
    )
@login_required
def applications_list(request):
    applications = AdmissionApplication.objects.all().order_by("-submitted_at")
    query = request.GET.get("q", "").strip()
    selected_status = request.GET.get("status", "").strip()
    if query:
        from django.db.models import Q
        applications = applications.filter(
            Q(application_number__icontains=query)
            | Q(application_reference__icontains=query)
            | Q(pupil_first_name__icontains=query)
            | Q(pupil_last_name__icontains=query)
            | Q(parent_full_name__icontains=query)
        )
    valid_statuses = ["pending", "reviewing", "accepted", "waitlisted", "rejected"]
    if selected_status in valid_statuses:
        applications = applications.filter(status=selected_status)
    return render(request, "admissions/applications_list.html", {
        "applications": applications,
        "query": query,
        "selected_status": selected_status,
    })
