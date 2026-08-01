from django.db import models

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

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"
        ordering = ["title"]

    def __str__(self):
        return self.title


# class Specialization(models.Model):
#     title = models.CharField(
#         max_length=50,
#         verbose_name="Краткое наименование специальности врача",
#         help_text="Краткое наименование специальности врача",
#     )
#
#     name = models.CharField(
#         max_length=150,
#         verbose_name="Полное наименование специальности врача",
#         help_text="Полное наименование специальности врача",
#     )
#
#     class Meta:
#         verbose_name = "Специальность"
#         verbose_name_plural = "Специальности"
#         ordering = ["title"]
#
#     def __str__(self):
#         return self.title
#

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

    # specialization = models.ForeignKey(
    #     Specialization,
    #     on_delete=models.CASCADE,
    #     related_name="specialization_doctor",
    #     verbose_name="Специальность",
    #     help_text="Специальность врача",
    # )

    specialization = models.CharField(
        max_length=50,
        verbose_name="Специальность",
        help_text="Укажите специальность врача",
    )

    foto = models.ImageField(
        upload_to="media/foto_doctor",
        blank=True,
        null=True,
        verbose_name="Фотография врача",
        help_text="Прикрепите фотографию врача",
        default="media/foto_doctor/default.jpg",
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

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"
        ordering = ["patient", "services"]

    def __str__(self):
        return f"{self.patient} {self.services} {self.datetime} {self.status}"
