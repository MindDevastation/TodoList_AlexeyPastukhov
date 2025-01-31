from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from .models import Task, Tag


class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["content", "deadline", "tags"]

        widgets = {
            #DateTime widget
            "deadline": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            #Checkbox
            "tags": forms.CheckboxSelectMultiple(),
        }

class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ["name"]


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]