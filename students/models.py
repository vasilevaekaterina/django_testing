from django.db import models


class Student(models.Model):

    name = models.CharField(max_length=255, verbose_name='Имя')

    birth_date = models.DateField(
        verbose_name='Дата рождения'
    )

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'

    def __str__(self):
        return self.name


class Course(models.Model):

    name = models.CharField(max_length=255, verbose_name='Название')
    students = models.ManyToManyField(
        Student,
        related_name='courses',
        blank=True,
        verbose_name='Студенты'
        )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'

    def __str__(self):
        return self.name
