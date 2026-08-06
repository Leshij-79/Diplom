from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory
from django.urls import reverse

from django.views.generic import TemplateView

from meddiag.mixins import CompanyInfoMixin
from meddiag.models import AboutCompany, Contacts, Direction, Services, Doctors
from meddiag.views import IndexListView, ServicesListView, DoctorsListView


class TestView(CompanyInfoMixin, TemplateView):
    template_name = 'test.html'


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
        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = TestView()
        view.request = request

        context = view.get_context_data()

        self.assertIn('about_company', context)
        self.assertIn('contacts', context)
        self.assertEqual(context['about_company'], self.about)
        self.assertEqual(context['contacts'], self.contacts)

    def test_company_info_mixin_no_data_context(self):
        AboutCompany.objects.all().delete()
        Contacts.objects.all().delete()

        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = TestView()
        view.request = request

        context = view.get_context_data()

        self.assertIsNone(context['about_company'])
        self.assertIsNone(context['contacts'])


class IndexListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.direction = Direction.objects.create(
            title="МРТ",
            name="МРТ",
        )

    def test_index_view(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = IndexListView()
        view.request = request
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertIn('direction_list', context)
        self.assertEqual(len(context['direction_list']), 1)
        self.assertEqual(context['direction_list'][0], self.direction)

    def test_index_view_with_second_direction(self):
        Direction.objects.create(
            title="КТ",
            name="КТ",
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = IndexListView()
        view.request = request
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(len(context['direction_list']), 2)

    def test_index_view_code_status(self):
        response = self.client.get(reverse('meddiag:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


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
        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = ServicesListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertIn('services_list', context)
        self.assertEqual(len(context['services_list']), 1,)
        self.assertEqual(context['services_list'][0], self.service)

    def test_services_list_view_with_second_service(self):
        Services.objects.create(
            title="КТ",
            name="КТ",
            direction=self.direction,
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = ServicesListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(len(context['services_list']), 2)

    def test_services_list_view_code_status(self):
        response = self.client.get(reverse('meddiag:services_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'services_list.html')


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
        response = self.client.get(reverse('meddiag:service_detail', kwargs={"pk": self.service.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service_detail.html')
        self.assertIn('service', response.context)
        self.assertEqual(response.context['service'], self.service)

    def test_service_detail_view_with_doctor(self):
        response = self.client.get(reverse('meddiag:service_detail', kwargs={"pk": self.service.pk})
                                   + f'?doctor_id={self.doctor.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'service_detail.html')
        self.assertIn('doctors', response.context)
        self.assertEqual(response.context['doctors'][0], self.doctor)

    def test_service_detail_view_no_service(self):
        response = self.client.get(reverse('meddiag:service_detail', kwargs={"pk": 666}))
        self.assertEqual(response.status_code, 404)

    def test_service_detail_view_context(self):
        # Проверка наличия всех необходимых данных в контексте
        response = self.client.get(
            reverse('meddiag:service_detail', kwargs={'pk': self.service.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('service', response.context)
        self.assertIn('doctors', response.context)
        self.assertIn('from_doctor_page', response.context)
        self.assertIn('about_company', response.context)
        self.assertIn('contacts', response.context)


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
        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = DoctorsListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertIn('doctors_list', context)
        self.assertEqual(len(context['doctors_list']), 1)
        self.assertEqual(context['doctors_list'][0], self.doctor)

    def test_doctors_list_view_with_second_doctor(self):
        Doctors.objects.create(
            last_name="Петров",
            first_name="Петр",
            middle_name="Петрович",
            specialization="Кардиолог",
            direction=self.direction,
        )

        request = self.factory.get('/')
        request.user = AnonymousUser()
        view = DoctorsListView()
        view.request = request
        view.kwargs = {"pk": 0}
        view.object_list = view.get_queryset()

        context = view.get_context_data()

        self.assertEqual(len(context['doctors_list']), 2)

    def test_services_list_view_code_status(self):
        response = self.client.get(reverse('meddiag:doctors_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doctors_list.html')
