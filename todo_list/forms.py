from django import forms
from django.contrib.auth.models import User

from .models import TodoPermission, ToDo


class PermissionForm(forms.ModelForm):
    class Meta:
        model = TodoPermission
        # fields = '__all__'
        fields = ['todo', 'user', 'reading', 'updating', 'deleting']

    user = forms.ModelChoiceField(queryset=User.objects.all(), label='Пользователь')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['todo'].queryset = ToDo.objects.filter(user=user)

