from django.contrib.auth import logout, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView

from .forms import PermissionForm
from .models import ToDo, TodoPermission


# Create your views here.

class ToDoList(LoginRequiredMixin, ListView):
    model = ToDo
    template_name = 'todo_list/todo_list.html'
    context_object_name = 'todo_list'

    def get_queryset(self):
        user = self.request.user
        return ToDo.objects.filter(Q(todopermission__user=user, todopermission__reading=True)).distinct()


class ToDoDetail(LoginRequiredMixin, DetailView):
    model = ToDo
    template_name = 'todo_list/todo.html'
    context_object_name = 'todo'

    def dispatch(self, request, *args, **kwargs):
        # Проверим, есть ли у пользователя право на просмотр данной задачи. Если прав нет, выйдет ошибка 403
        todo = self.get_object()
        user = request.user

        if not todo.user == user:
            #у автора права всегда есть
            try:
                permission = TodoPermission.objects.get(user=user, todo=todo)
                if not permission.reading:
                    raise PermissionDenied
            except TodoPermission.DoesNotExist:
                raise PermissionDenied

        return super(ToDoDetail, self).dispatch(request, *args, **kwargs)


class ToDoCreate(LoginRequiredMixin, CreateView):
    model = ToDo
    fields = ['title', 'description', 'is_done']
    template_name = 'todo_list/todo_update.html'

    success_url = reverse_lazy('todo_list')

    def form_valid(self, form):
        form.instance.user = self.request.user

        response = super(ToDoCreate, self).form_valid(form)

        # Сразу создадим запись со всеми правами для автора задачи
        TodoPermission.objects.create(
            user=self.request.user,
            todo=form.instance,
            reading=True,
            updating=True,
            deleting=True
        )

        return response


class ToDoUpdate(LoginRequiredMixin, UpdateView):
    model = ToDo
    template_name = 'todo_list/todo_update.html'
    context_object_name = 'todo'
    fields = ['title', 'description', 'is_done']
    success_url = reverse_lazy('todo_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверим, есть ли у пользователя право на изменение данной задачи. Если прав нет, выйдет ошибка 403
        todo = self.get_object()
        user = request.user

        # у автора права всегда есть
        if not todo.user == user:
            try:
                permission = TodoPermission.objects.get(user=user, todo=todo)
                if not permission.updating:
                    raise PermissionDenied
            except TodoPermission.DoesNotExist:
                raise PermissionDenied

        return super(ToDoUpdate, self).dispatch(request, *args, **kwargs)


class ToDoDelete(LoginRequiredMixin, DeleteView):
    model = ToDo
    context_object_name = 'todo'
    success_url = reverse_lazy('todo_list')

    def dispatch(self, request, *args, **kwargs):
        # Проверим, есть ли у пользователя право на удаление данной задачи. Если прав нет, выйдет ошибка 403
        todo = self.get_object()
        user = request.user

        # у автора права всегда есть
        if not todo.user == user:
            try:
                permission = TodoPermission.objects.get(user=user, todo=todo)
                if not permission.updating:
                    raise PermissionDenied
            except TodoPermission.DoesNotExist:
                raise PermissionDenied

        return super(ToDoDelete, self).dispatch(request, *args, **kwargs)


class UserLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'todo_list/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('todo_list')


def logout_user(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


class UserRegister(FormView):
    template_name = 'todo_list/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('todo_list')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(UserRegister, self).form_valid(form)


class ToDoPermissionsView(LoginRequiredMixin, TemplateView):
    template_name = 'todo_list/todo_permissions_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        todos = ToDo.objects.filter(user=self.request.user)
        permissions = TodoPermission.objects.all()
        todo_permissions = {}

        for todo in todos:
            todo_permissions[todo] = []
            for permission in permissions.filter(todo=todo).exclude(user=self.request.user):

                permission.can_delete = True
                todo_permissions[todo].append(permission)

        context['todo_permissions'] = todo_permissions
        return context


class TodoPermissionCreateView(LoginRequiredMixin, CreateView):
    model = TodoPermission
    form_class = PermissionForm
    template_name = 'todo_list/add_permission.html'
    success_url = reverse_lazy('task_permissions')

    def get_form_kwargs(self):
        # Отправим текущего пользователя в класс формы, чтобы по нему установить фильтр к полям
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class TodoPermissionDeleteView(LoginRequiredMixin, DeleteView):
    model = TodoPermission
    template_name = 'todo_list/delete_permission.html'
    success_url = reverse_lazy('task_permissions')

    def get_queryset(self):
        queryset = super().get_queryset()
        # Ensure that the user can only delete permissions they own or have access to
        return queryset.filter(todo__user=self.request.user).exclude(user=self.request.user)

