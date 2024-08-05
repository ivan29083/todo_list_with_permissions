from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class ToDo(models.Model):
    title = models.CharField('Название', max_length=80)
    description = models.TextField('Содержание', max_length=500)
    is_done = models.BooleanField('Выполнено', default=False)
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['is_done']

    def __str__(self):
        return self.title


class TodoPermission(models.Model):
    todo = models.ForeignKey(ToDo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reading = models.BooleanField('Чтение', default=False)
    updating = models.BooleanField('Обновление', default=False)
    deleting = models.BooleanField('Удаление', default=False)

    class Meta:
        verbose_name = 'Доступ пользователя к задаче'
        verbose_name_plural = 'Доступы пользователей к задачам'
        unique_together = ('user', 'todo')

    def __str__(self):
        return f'Доступ {self.user} к {self.task}'
