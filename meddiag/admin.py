from django.contrib import admin

from meddiag.models import Direction, Services, Doctors, Appointment


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "name",
    )

    list_filter = (
        "name",
    )

    search_fields = (
        "name",
    )


@admin.register(Services)
class ServicesAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "name",
        "description",
        "price",
        "duration_execution",
        "direction",
    )

    list_filter = (
        "title",
        "name",
        "direction",
    )

    search_fields = (
        "title",
        "name",
    )


@admin.register(Doctors)
class DoctorsAdmin(admin.ModelAdmin):
    list_display = (
        "last_name",
        "first_name",
        "middle_name",
        "category",
        "experience",
        "specialization",
        "direction",
        "foto",
    )

    list_filter = (
        "last_name",
        "specialization",
        "direction",
    )

    search_fields = (
        "last_name",
    )


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient",
        "doctor",
        "services",
        "status",
        "datetime",
    )

    list_filter = (
        "patient",
        "doctor",
        "services",
        "status",
    )

    search_fields = (
        "patient",
        "doctor",
        "services",
    )
