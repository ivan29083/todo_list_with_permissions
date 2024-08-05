from django import forms
from django.contrib.auth import get_user_model

from .models import TodoPermission, ToDo


class PermissionForm(forms.ModelForm):
    class Meta:
        model = TodoPermission
        fields = ['todo', 'user', 'reading', 'updating', 'deleting']

    user_model = get_user_model()
    user = forms.ModelChoiceField(queryset=user_model.objects.all(), label='Пользователь')

    def __init__(self, *args, **kwargs):
        # если в форму передан пользователь, то в поле 'todo' будут только задачи, где он автор.
        #  И в поле user он отображаться не будет
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            user_model = get_user_model()
            self.fields['todo'].queryset = ToDo.objects.filter(user=user)
            self.fields['user'].queryset = user_model.objects.exclude(pk=user.pk)

