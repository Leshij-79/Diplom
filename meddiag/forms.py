from django import forms

from meddiag.models import Appointment, Doctors


class AppointmentForm(forms.ModelForm):
    """
    Форма для записи на прием
    """
    class Meta:
        model = Appointment
        fields = ['services', 'doctor', 'datetime']
        widgets = {
            'datetime': forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            'services': forms.Select(attrs={'class': 'form-control', 'id': 'id_service'}),
            'doctor': forms.Select(attrs={'class': 'form-control', 'id': 'id_doctor'}),
        }
        labels = {
            'services': 'Услуга',
            'doctor': 'Врач',
            'datetime': 'Дата и время',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        service_id = None

        if 'services' in self.data:
            try:
                service_id = int(self.data.get('services'))
            except (ValueError, TypeError):
                pass
        elif self.initial and 'services' in self.initial:
            service_id = self.initial.get('services')
        elif self.instance.pk:
            service_id = self.instance.services_id

        if service_id:
            try:
                self.fields['doctor'].queryset = Doctors.objects.filter(
                    doctors_service__id=service_id
                ).distinct()
            except (ValueError, TypeError):
                self.fields['doctor'].queryset = Doctors.objects.all()
        elif self.instance.pk:
            self.fields['doctor'].queryset = self.instance.services.doctors.all()
        else:
            self.fields['doctor'].queryset = Doctors.objects.all()


class ContactForm(forms.Form):
    """
    Форма обратной связи
    """

    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Иванов Иван", "class": "form-control"}),
        label="Ваше имя",
    )
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(attrs={"placeholder": "example@mail.ru", "class": "form-control"}),
        label="Email",
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "+7 (999) 123-45-67", "class": "form-control"}),
        label="Телефон",
    )
    subject = forms.ChoiceField(
        choices=[
            ("appointment", "Запись на прием"),
            ("question", "Вопрос по услугам"),
            ("complaint", "Жалоба или предложение"),
            ("cooperation", "Сотрудничество"),
            ("other", "Другое"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Тема обращения",
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"rows": 6, "placeholder": "Опишите ваш вопрос или обращение...", "class": "form-control"}
        ),
        label="Сообщение",
    )
