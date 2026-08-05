from django.contrib import admin

from meddiag.models import Direction, Services, Doctors, Appointment, AboutCompany, Contacts


@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
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
        "pk",
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
        "pk",
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
        "pk",
        "patient",
        "doctor",
        "services",
        "status",
        "datetime",
        "result",
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


@admin.register(AboutCompany)
class AboutCompanyAdmin(admin.ModelAdmin):
    list_display = (
        "small_name",
        "full_name",
        "slogan",
        "history",
        "mission",
        "doctors",
        "image",
        "small_image",
    )

    list_filter = (
        "small_name",
    )

    search_fields = (
        "small_name",
    )


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = (
        "phone",
        "email",
        "address",
        "work_days",
        "hour_start",
        "hour_end",
        "work_days_second",
        "hour_start_second",
        "hour_end_second",
        "weekend",
        "map",
    )

    list_filter = (
        "phone",
    )

    search_fields = (
        "phone",
    )
