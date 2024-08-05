from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.ToDoList.as_view(), name='todo_list'),

    path('create/', views.ToDoCreate.as_view(), name='create'),
    path('todo/<int:pk>', views.ToDoDetail.as_view(), name='todo'),
    path('update/<int:pk>', views.ToDoUpdate.as_view(), name='update'),
    path('delete/<int:pk>', views.ToDoDelete.as_view(), name='delete'),

    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.UserRegister.as_view(), name='register'),

    path('task_permissions/', views.ToDoPermissionsView.as_view(), name='task_permissions'),
    path('add_permission/', views.TodoPermissionCreateView.as_view(), name='add_permission'),
    path('delete_permission/<int:pk>/', views.TodoPermissionDeleteView.as_view(), name='delete_permission'),

]