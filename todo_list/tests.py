from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from .models import ToDo


# Create your tests here.
class GetTodoTest(TestCase):
    # python -Xutf8 manage.py dumpdata todo_list.todo -o todo_list/fixtures/todo_list_todo.json
    # python -Xutf8 manage.py dumpdata todo_list.TodoPermission -o todo_list/fixtures/todo_list_TodoPermission.json
    # python -Xutf8 manage.py dumpdata auth.user -o todo_list/fixtures/auth_user.json

    fixtures = ['todo_list_todo.json', 'todo_list_TodoPermission.json', 'auth_user.json']

    def setUp(self):
        "Инициализация перед выполнением каждого теста"
        self.login_url = reverse('login')
        self.main_page_url = reverse('todo_list')

        user_model = get_user_model()
        users = user_model.objects.all()
        if users:
            for user in users:
                user.set_password('testpassword')
                user.save()

    def test_redirect_addpage(self):
        # незалогированного пользователя с главной страницы перенаправит на страницу login

        path = self.main_page_url
        redirect_uri = reverse('login') + '?next=' + path
        response = self.client.get(path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, redirect_uri)

    def test_login_and_access_main_page(self):
        # Логин под пользователем
        user_model = get_user_model()

        user = user_model.objects.get(pk=1)
        login_successful = self.client.login(username=user.username, password='testpassword')
        self.assertTrue(login_successful, "Login failed")

        # Переходим на главную страницу
        response = self.client.get(self.main_page_url)
        self.assertEqual(response.status_code, HTTPStatus.OK, "Main page is not accessible")
        self.assertTemplateUsed(response, 'todo_list/todo_list.html')

        # Сравниваем список задач, отображаемых пользователю
        todos = ToDo.objects.filter(Q(todopermission__user=user, todopermission__reading=True)).distinct()
        self.assertQuerysetEqual(response.context_data['todo_list'], todos)
