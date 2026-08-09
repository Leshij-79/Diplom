from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.core import mail
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from django.views.generic import TemplateView

from meddiag.mixins import CompanyInfoMixin
from meddiag.models import AboutCompany, Appointment, Contacts, Direction, Doctors, Services
from meddiag.views import DoctorsListView, IndexListView, ServicesListView
from users.models import CustomUser


class TestView(CompanyInfoMixin, TemplateView):
    template_name = "test.html"


class CompanyInfoMixinTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.about = AboutCompany.objects.first()
        self.contacts = Contacts.objects.first()

        self.about = AboutCompany.objects.create(
            small_name="МедДиагностика",
            full_name="Медицинская Диагностика",
            slogan="Забота о вашем здоровье",
            history="История компании",
            mission="Наша миссия",
            doctors="Наши врачи",
        )
        self.contacts = Contacts.objects.create(
            phone="+7 (495) 123-45-67",
            email="info@meddiagnostic.ru",
            address="г. Москва, ул. Медицинская, 10",
            work_days="Пн-Пт",
            hour_start=8,
            hour_end=20,
            work_days_second="Сб",
            hour_start_second=9,
            hour_end_second=18,
            weekend="Вс",
        )

    def test_company_info_mixin_context(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = TestView()
        view.request = request

        context = view.get_context_data()

        self.assertIn("about_company", context)
        self.assertIn("contacts", context)
        self.assertEqual(context["about_company"], self.about)
        self.assertEqual(context["contacts"], self.contacts)

    def test_company_info_mixin_no_data_context(self):
        AboutCompany.objects.all().delete()
        Contacts.objects.all().delete()

        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = TestView()
        view.request = request

        context = view.get_context_data()

        self.assertIsNone(context["about_company"])
        self.assertIsNone(context["contacts"])


class IndexListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.direction = Direction.objects.create(
            title="МРТ",
            name="МРТ",
        )

    def test_index_view(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = IndexListView()
        view.request = request
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertIn("direction_list", context)
        self.assertEqual(len(context["direction_list"]), 1)
        self.assertEqual(context["direction_list"][0], self.direction)

    def test_index_view_with_second_direction(self):
        Direction.objects.create(
            title="КТ",
            name="КТ",
        )

        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = IndexListView()
        view.request = request
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(len(context["direction_list"]), 2)

    def test_index_view_code_status(self):
        response = self.client.get(reverse("meddiag:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")


class ServicesListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.direction = Direction.objects.create(
            title="МРТ",
            name="МРТ",
        )
        self.service = Services.objects.create(
            title="МРТ",
            name="МРТ",
            direction=self.direction,
        )

    def test_services_list_view(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = ServicesListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertIn("services_list", context)
        self.assertEqual(
            len(context["services_list"]),
            1,
        )
        self.assertEqual(context["services_list"][0], self.service)

    def test_services_list_view_with_second_service(self):
        Services.objects.create(
            title="КТ",
            name="КТ",
            direction=self.direction,
        )

        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = ServicesListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(len(context["services_list"]), 2)

    def test_services_list_view_code_status(self):
        response = self.client.get(reverse("meddiag:services_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "services_list.html")


class ServiceDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.direction = Direction.objects.create(
            title="МРТ",
            name="МРТ",
        )
        self.service = Services.objects.create(
            title="МРТ",
            name="МРТ",
            direction=self.direction,
        )
        self.doctor = Doctors.objects.create(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
            specialization="Кардиолог",
            direction=self.direction,
        )
        self.service.doctors.add(self.doctor)

    def test_service_detail_view(self):
        response = self.client.get(reverse("meddiag:service_detail", kwargs={"pk": self.service.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "service_detail.html")
        self.assertIn("service", response.context)
        self.assertEqual(response.context["service"], self.service)

    def test_service_detail_view_with_doctor(self):
        response = self.client.get(
            reverse("meddiag:service_detail", kwargs={"pk": self.service.pk}) + f"?doctor_id={self.doctor.pk}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "service_detail.html")
        self.assertIn("doctors", response.context)
        self.assertEqual(response.context["doctors"][0], self.doctor)

    def test_service_detail_view_no_service(self):
        response = self.client.get(reverse("meddiag:service_detail", kwargs={"pk": 666}))
        self.assertEqual(response.status_code, 404)

    def test_service_detail_view_context(self):
        # Проверка наличия всех необходимых данных в контексте
        response = self.client.get(reverse("meddiag:service_detail", kwargs={"pk": self.service.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("service", response.context)
        self.assertIn("doctors", response.context)
        self.assertIn("from_doctor_page", response.context)
        self.assertIn("about_company", response.context)
        self.assertIn("contacts", response.context)


class DoctorsListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.direction = Direction.objects.create(
            title="Кардиология",
            name="Кардиология",
        )
        self.doctor = Doctors.objects.create(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
            specialization="Кардиолог",
            direction=self.direction,
        )

    def test_doctors_list_view(self):
        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = DoctorsListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertIn("doctors_list", context)
        self.assertEqual(len(context["doctors_list"]), 1)
        self.assertEqual(context["doctors_list"][0], self.doctor)

    def test_doctors_list_view_with_second_doctor(self):
        Doctors.objects.create(
            last_name="Петров",
            first_name="Петр",
            middle_name="Петрович",
            specialization="Кардиолог",
            direction=self.direction,
        )

        request = self.factory.get("/")
        request.user = AnonymousUser()
        view = DoctorsListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(len(context["doctors_list"]), 2)

    def test_services_list_view_code_status(self):
        response = self.client.get(reverse("meddiag:doctors_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctors_list.html")


class DoctorDetailViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.direction = Direction.objects.create(
            title="Кардиология",
            name="Кардиология",
        )
        self.doctor = Doctors.objects.create(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
            specialization="Кардиолог",
            direction=self.direction,
        )
        self.service = Services.objects.create(
            title="Кардиология",
            name="Кардиология",
            direction=self.direction,
        )
        self.service.doctors.add(self.doctor)

    def test_doctor_detail_view(self):
        response = self.client.get(reverse("meddiag:doctor_detail", kwargs={"pk": self.doctor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor_detail.html")
        self.assertIn("doctor", response.context)
        self.assertEqual(response.context["doctor"], self.doctor)

    def test_doctor_detail_view_with_service(self):
        response = self.client.get(
            reverse("meddiag:doctor_detail", kwargs={"pk": self.doctor.pk}) + f"?service_id={self.service.pk}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doctor_detail.html")
        self.assertIn("services", response.context)
        self.assertEqual(response.context["services"][0], self.service)

    def test_doctor_detail_view_no_doctor(self):
        response = self.client.get(reverse("meddiag:doctor_detail", kwargs={"pk": 666}))
        self.assertEqual(response.status_code, 404)

    def test_doctor_detail_view_context(self):
        # Проверка наличия всех необходимых данных в контексте
        response = self.client.get(reverse("meddiag:doctor_detail", kwargs={"pk": self.doctor.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn("services", response.context)
        self.assertIn("doctor", response.context)
        self.assertIn("from_service_page", response.context)
        self.assertIn("about_company", response.context)
        self.assertIn("contacts", response.context)


class AppointmentCreateViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
        )

        self.contacts = Contacts.objects.create(
            phone="+7 (495) 123-45-67",
            email="info@meddiagnostic.ru",
            address="г. Москва, ул. Медицинская, 10",
            work_days="Пн-Пт",
            hour_start="8",
            hour_end="20",
            work_days_second="Сб",
            hour_start_second="9",
            hour_end_second="18",
            weekend="Вс",
        )

        self.direction = Direction.objects.create(
            title="Кардиология",
            name="Кардиология",
        )
        self.doctor = Doctors.objects.create(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
            specialization="Кардиолог",
            direction=self.direction,
        )
        self.service = Services.objects.create(
            title="Кардиология",
            name="Кардиология",
            direction=self.direction,
        )
        self.service.doctors.add(self.doctor)

    def test_appointment_create_view(self):
        self.client.login(username="test@test.ru", password="testpass123")

        response = self.client.get(
            reverse("meddiag:appointment_create"), {"doctor": self.doctor.pk, "service": self.service.pk}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointment_create.html")
        self.assertIn("services", response.context)
        self.assertIn("doctor_for_service", response.context)

    def test_appointment_create_view_without_params(self):
        self.client.login(username="test@test.ru", password="testpass123")

        response = self.client.get(reverse("meddiag:appointment_create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointment_create.html")
        self.assertIsNone(response.context.get("selected_service"))
        self.assertIsNone(response.context.get("selected_doctor"))

    def test_appointment_create_view_requires_login(self):
        response = self.client.get(reverse("meddiag:appointment_create"))

        self.assertEqual(response.status_code, 302)

    def test_form_valid(self):
        self.client.force_login(self.user)

        future_datetime = timezone.now() + timedelta(days=1)

        url = reverse("meddiag:appointment_create")

        data = {
            "services": self.service.id,
            "doctor": self.doctor.id,
            "datetime": future_datetime.strftime("%Y-%m-%d %H:%M"),
        }

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)

        appointment = Appointment.objects.filter(
            patient=self.user, doctor=self.doctor, services=self.service, status="active"
        ).first()
        self.assertIsNotNone(appointment)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Запись на приём")
        self.assertEqual(mail.outbox[0].to[0], self.user.email)

    def test_form_valid_with_invalid_doctor(self):
        self.client.force_login(self.user)

        future_datetime = timezone.now() + timedelta(days=1)

        url = reverse("meddiag:appointment_create")

        data = {
            "services": self.service.id,
            "doctor": 666,
            "datetime": future_datetime.strftime("%Y-%m-%d %H:%M"),
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)

    def test_get_initial_with_params(self):
        self.client.force_login(self.user)

        url = reverse("meddiag:appointment_create")
        response = self.client.get(url, {"service": self.service.id, "doctor": self.doctor.id})

        self.assertEqual(response.status_code, 200)

    def test_get_initial_without_params(self):
        self.client.force_login(self.user)

        url = reverse("meddiag:appointment_create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.context.get("selected_service"))
        self.assertIsNone(response.context.get("selected_doctor"))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
        )

    def test_get_object(self):
        self.client.login(username="test@test.ru", password="testpass123")

        response = self.client.get(reverse("meddiag:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")


class AppointmentCancelViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
        )

        self.contacts = Contacts.objects.create(
            phone="+7 (495) 123-45-67",
            email="info@meddiagnostic.ru",
            address="г. Москва, ул. Медицинская, 10",
            work_days="Пн-Пт",
            hour_start="8",
            hour_end="20",
            work_days_second="Сб",
            hour_start_second="9",
            hour_end_second="18",
            weekend="Вс",
        )

        self.direction = Direction.objects.create(
            title="Кардиология",
            name="Кардиология",
        )
        self.doctor = Doctors.objects.create(
            last_name="Иванов",
            first_name="Иван",
            middle_name="Иванович",
            specialization="Кардиолог",
            direction=self.direction,
        )
        self.service = Services.objects.create(
            title="Кардиология",
            name="Кардиология",
            direction=self.direction,
        )
        self.service.doctors.add(self.doctor)

        self.appointment = Appointment.objects.create(
            patient=self.user,
            doctor=self.doctor,
            services=self.service,
            status="active",
            datetime=timezone.now() + timedelta(days=1),
        )

    def test_post(self):
        self.client.login(username="test@test.ru", password="testpass123")

        url = reverse("meddiag:appointment_cancel", kwargs={"pk": self.appointment.pk})

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "appointment_detail.html")

        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, "cancel")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Отмена записи на приём")
        self.assertEqual(mail.outbox[0].to[0], self.user.email)


class ContactFormViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@test.ru",
            first_name="Test",
            last_name="User",
            middle_name="User",
            phone_number="71234567890",
        )

        self.contacts = Contacts.objects.create(
            phone="+7 (495) 123-45-67",
            email="info@meddiagnostic.ru",
            address="г. Москва, ул. Медицинская, 10",
            work_days="Пн-Пт",
            hour_start="8",
            hour_end="20",
            work_days_second="Сб",
            hour_start_second="9",
            hour_end_second="18",
            weekend="Вс",
        )

        self.about = AboutCompany.objects.create(
            small_name="Test",
            full_name="Test",
            slogan="Test slogan",
            history="Test history",
            mission="Test mission",
            doctors="Test doctors",
        )

    def test_send_email(self):
        url = reverse("meddiag:contact_form")

        data = {
            "name": self.user.first_name,
            "email": self.user.email,
            "phone": self.user.phone_number,
            "subject": "question",
            "message": "Test message",
        }

        response = self.client.post(url, data, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form_success.html")

        self.assertEqual(len(mail.outbox), 2)

        self.assertEqual(mail.outbox[0].subject, "Сообщение с формы обратной связи")
        self.assertEqual(mail.outbox[0].to[0], self.contacts.email)

        self.assertEqual(mail.outbox[1].subject, f"Копия вашего обращения в {self.about.small_name}")
        self.assertEqual(mail.outbox[1].to[0], self.user.email)

    def test_contact_form_view_get(self):
        response = self.client.get(reverse("meddiag:contact_form"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form.html")
        self.assertIn("form", response.context)

    def test_contact_form_without_required_fields(self):
        url = reverse("meddiag:contact_form")

        response = self.client.post(url, {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form.html")

        self.assertEqual(len(mail.outbox), 0)

    def test_contact_form_success_view(self):
        self.client.login(username="test@test.ru", password="testpass123")

        response = self.client.get(reverse("meddiag:contact_form_success"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form_success.html")
