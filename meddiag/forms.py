from django import forms


class AppointmentForm(forms.Form):
    """Форма для записи на прием"""

    datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )


class ContactForm(forms.Form):
    """Форма обратной связи"""

    name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Иванов Иван", "class": "form-control"}),
        label="Ваше имя",
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"placeholder": "example@mail.ru", "class": "form-control"}), label="Email"
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
