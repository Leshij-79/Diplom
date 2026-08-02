from django import forms
from meddiag.models import Appointment, Services, Doctors


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['services', 'doctor', 'datetime']
        widgets = {
            'datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Фильтруем врачей по выбранной услуге
        if 'services' in self.data:
            try:
                service_id = int(self.data.get('services'))
                self.fields['doctor'].queryset = Doctors.objects.filter(
                    doctors_service__id=service_id
                ).distinct()
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['doctor'].queryset = self.instance.services.doctors.all()