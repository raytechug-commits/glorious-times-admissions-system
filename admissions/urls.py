
from django.urls import path
from . import views

app_name = "admissions"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("applications/", views.applications_list, name="applications_list"),
    path("applications/add/", views.add_application, name="add_application"),
    path("applications/<int:application_id>/", views.review_application, name="review_application"),
    path("applications/<int:application_id>/status/", views.update_application_status, name="update_application_status"),
    path("apply/", views.public_apply, name="public_apply"),
    path(
        "apply/confirmation/<str:reference>/",
        views.application_confirmation,
        name="confirmation",
    ),
]


