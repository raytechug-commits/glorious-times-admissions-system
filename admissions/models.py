
from django.db import models
from django.utils import timezone


class AdmissionApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("reviewing", "Under Review"),
        ("accepted", "Accepted"),
        ("waitlisted", "Waitlisted"),
        ("rejected", "Not Accepted"),
    ]

    # Kept to preserve the existing application's original number.
    application_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    # Generated when an application is submitted.
    application_reference = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    # Generated only after the school accepts the application.
    admission_number = models.CharField(
        max_length=20, unique=True, blank=True, null=True
    )

    pupil_first_name = models.CharField(max_length=100)
    pupil_middle_name = models.CharField(max_length=100, blank=True)
    pupil_last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20, blank=True)
    class_applying_for = models.CharField(max_length=50)
    previous_school = models.CharField(max_length=200, blank=True)
    medical_information = models.TextField(blank=True)

    parent_full_name = models.CharField(max_length=200)
    parent_email = models.EmailField(blank=True)
    parent_phone = models.CharField(max_length=30)
    parent_relationship = models.CharField(max_length=50, blank=True)

    father_full_name = models.CharField(max_length=200, blank=True)
    father_relationship = models.CharField(max_length=50, blank=True)
    father_phone = models.CharField(max_length=30, blank=True)
    father_email = models.EmailField(blank=True)
    father_occupation = models.CharField(max_length=150, blank=True)

    mother_full_name = models.CharField(max_length=200, blank=True)
    mother_relationship = models.CharField(max_length=50, blank=True)
    mother_phone = models.CharField(max_length=30, blank=True)
    mother_email = models.EmailField(blank=True)
    mother_occupation = models.CharField(max_length=150, blank=True)

    residential_address = models.TextField()
    additional_information = models.TextField(blank=True)

    declaration_name = models.CharField(max_length=200, blank=True)
    declaration_date = models.DateField(null=True, blank=True)
    declaration_accepted = models.BooleanField(default=False)

    rejection_reason = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Preserve the old number if this record already has one.
        if self.parent_full_name and not self.parent_email:
            self.parent_email = ""

        super().save(*args, **kwargs)

    def __str__(self):
        reference = self.application_reference or self.application_number or "Unnumbered"
        return f"{reference} - {self.pupil_first_name} {self.pupil_last_name}"

    class Meta:
        ordering = ["-submitted_at"]

