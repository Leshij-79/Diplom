from django.db import models
from django_filters.utils import verbose_field_name

from users.models import CustomUser


class Direction(models.Model):
    """
    Модель направлений диагностики для группировки услуг по диагностике
    """
    title = models.CharField(
        max_length=50,
        verbose_name="Краткое наименование направления диагностики",
        help_text="Укажите краткое наименование направления диагностики",
    )

    name = models.CharField(
        max_length=150,
        verbose_name="Полное наименование направления диагностики",
        help_text="Укажите полное наименование направления диагностики",
    )

    image = models.ImageField(
        upload_to="static/images",
        blank=True,
        null=True,
        verbose_name="Иконка вида диагностики",
        help_text="Прикрепите иконку вида диагностики",
        default="media/images/default.jpg",
    )

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Doctors(models.Model):
    """
    Модель по врачам с указанием их специализации, стажа и направления диагностики
    """
    STATUS_CATEGORY = [
        ("highest", "Высшая категория"),
        ("first", "Первая категория"),
        ("second", "Вторая категория"),
        ("without","Без категории"),
    ]

    last_name = models.CharField(
        max_length=50,
        verbose_name="Фамилия",
        help_text="Укажите фамилию врача",
    )

    first_name = models.CharField(
        max_length=50,
        verbose_name="Имя",
        help_text="Укажите имя врача",
    )

    middle_name = models.CharField(
        max_length=50,
        verbose_name="Отчество",
        help_text="Укажите отчество врача",
    )

    category = models.CharField(
        max_length=7,
        choices=STATUS_CATEGORY,
        default="without",
        verbose_name="Категория врача",
        help_text="Выберите категорию врача",
    )

    experience = models.PositiveIntegerField(
        verbose_name="Стаж работы",
        help_text="Укажите стаж работы врача",
        default=0,
    )

    specialization = models.CharField(
        max_length=50,
        verbose_name="Специальность",
        help_text="Укажите специальность врача",
    )

    foto = models.ImageField(
        upload_to="foto_doctor/",
        blank=True,
        null=True,
        verbose_name="Фотография врача",
        help_text="Прикрепите фотографию врача",
        default="foto_doctor/default.jpg",
    )

    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        related_name="direction_doctor",
        verbose_name="Направление диагностики",
        help_text="Выберите направление диагностики",
    )

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ["last_name", "specialization"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name} {self.specialization}"


class Services(models.Model):
    """
    Модель услуг по диагностике
    """
    title = models.CharField(
        max_length=50,
        verbose_name="Краткое наименование услуги",
        help_text="Укажите краткое наименование услуги",
    )

    name = models.CharField(
        max_length=200,
        verbose_name="Полное наименование услуги",
        help_text="Укажите полное наименование услуги",
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание услуги",
        help_text="Укажите описание медицинской услуги",
    )

    price = models.PositiveIntegerField(
        verbose_name="Стоимость услуги",
        help_text="Укажите стоимость медицинской услуги",
        default=0,
    )

    duration_execution = models.PositiveIntegerField(
        verbose_name="Продолжительность услуги в минутах",
        help_text = "Укажите продолжительность выполнения медицинской услуги в минутах",
        default=10,
    )

    direction = models.ForeignKey(
        Direction,
        on_delete=models.CASCADE,
        related_name="direction_name",
        verbose_name="Направление диагностики",
        help_text="Выберите направление медицинской диагностики",
    )

    doctors = models.ManyToManyField(
        Doctors,
        related_name="doctors_service",
        verbose_name="Врачи оказывающие услугу",
        help_text="Укажите врачей оказывающих услугу",
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["title"]

    def __str__(self):
        return self.title


class Appointment(models.Model):
    """
    Модель записи на приём пациента
    """
    STATUS = [
        ("active", "Активная"),
        ("rendered", "Оказана"),
        ("cancel", "Отменена"),
    ]

    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="patient",
        verbose_name="Пациент",
        help_text="Выберите пациента",
    )

    doctor = models.ForeignKey(
        Doctors,
        on_delete=models.CASCADE,
        related_name="doctor",
        verbose_name="Врач",
        help_text="Выберите врача",
    )

    services = models.ForeignKey(
        Services,
        on_delete=models.CASCADE,
        related_name="services",
        verbose_name="Услуга",
        help_text="Выберите услугу",
    )

    status = models.CharField(
        max_length=8,
        choices=STATUS,
        default="active",
        verbose_name="Статус услуги",
    )

    datetime = models.DateTimeField(
        verbose_name="Время оказания услуги",
        help_text="Укажите время оказания услуги",
    )

    result = models.TextField(
        blank=True,
        null=True,
        verbose_name="Результат диагностики",
        help_text="Внесите результат диагностики",
        default='',
    )

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["patient", "services"]

    def __str__(self):
        return f"{self.patient} {self.services} {self.datetime} {self.status}"


class AboutCompany(models.Model):
    """
    Модель раздела О компании
    """
    small_name = models.CharField(
        max_length=100,
        verbose_name="Короткое название медицинской компании",
        help_text="Укажите короткое название медицинской компании",
    )

    full_name = models.CharField(
        max_length=250,
        verbose_name="Название полное медицинской компании",
        help_text="Укажите полное название медицинской компании",
    )

    slogan = models.TextField(
        verbose_name="Cлоган медицинской компании",
        help_text="Укажите слоган медицинской компании",
    )

    history = models.TextField(
        verbose_name="История медицинской компании",
        help_text="Укажите историю медицинской компании",
    )

    mission = models.TextField(
        verbose_name="Миссия и ценности",
        help_text="Укажите миссию и ценности",
    )

    doctors = models.TextField(
        verbose_name="Команда врачей",
        help_text="Опишите команду врачей",
    )

    image = models.ImageField(
        upload_to="settings/",
        blank=True,
        null=True,
        verbose_name="Эмблема медицинской компании",
        help_text="Прикрепите эмблему медицинской компании",
        default="settings/default.jpg",
    )

    small_image = models.ImageField(
        upload_to="settings/",
        blank=True,
        null=True,
        verbose_name="Эмблема маленькая медицинской компании",
        help_text="Прикрепите маленькую эмблему медицинской компании",
        default="settings/small_default.png",
    )

    class Meta:
        verbose_name = "О компании"
        verbose_name_plural = "О компании"
        ordering = ["small_name", "slogan"]

    def __str__(self):
        return f"{self.small_name} - {self.slogan}"


class Contacts(models.Model):
    """
    Модель контактной информации компании
    """
    phone = models.CharField(
        max_length=100,
        verbose_name="Телефон",
        help_text="Укажите номер телефона/ов",
    )

    email = models.CharField(
        max_length=100,
        verbose_name="Email",
        help_text="Укажите email",
    )

    address = models.TextField(
        verbose_name="Адрес",
        help_text="Укажите адрес медицинской компании",
    )

    work_days = models.CharField(
        max_length=30,
        verbose_name="Рабочие дни недели",
        help_text="Укажите рабочие дни недели",
    )

    hour_start = models.CharField(
        max_length=2,
        verbose_name="Час начала работы",
        help_text="Укажите час начала работы",
    )

    hour_end = models.CharField(
        max_length=2,
        verbose_name="Час окончания работы",
        help_text="Укажите час окончания работы",
    )

    work_days_second = models.CharField(
        max_length=30,
        verbose_name="Не основные рабочие дни недели",
        help_text="Укажите не основные рабочие дни недели",
    )

    hour_start_second = models.CharField(
        max_length=2,
        verbose_name="Не основной час начала работы",
        help_text="Укажите не основной час начала работы",
    )

    hour_end_second = models.CharField(
        max_length=2,
        verbose_name="Не основной час окончания работы",
        help_text="Укажите не основой час окончания работы",
    )

    weekend = models.CharField(
        max_length=30,
        verbose_name="выходные дни недели",
        help_text="Укажите выходные дни недели",
    )

    map = models.TextField(
        blank=True,
        null=True,
        verbose_name="Код iframe cкрипт карты",
        help_text="Вставьте код iframe скрипт карты",
    )

    class Meta:
        verbose_name = "Настройки компании"
        verbose_name_plural = "Настройки компании"
        ordering = ["phone"]

    def __str__(self):
        return f"{self.phone}"
