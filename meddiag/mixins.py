from meddiag.models import AboutCompany, Contacts


class CompanyInfoMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        about = AboutCompany.objects.first()
        context['about_company'] = about

        contacts = Contacts.objects.first()
        context['contacts'] = contacts

        return context