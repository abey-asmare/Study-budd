from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Message, Room


class CreateUser(UserCreationForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class UpdateProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    username = forms.CharField(max_length=20)
    email = forms.EmailField()
    avatar = forms.ImageField()

    class Meta(User):
        model = UserProfile
        fields = ['avatar', 'first_name', 'last_name', 'username', 'email', 'about']


class CommentForm(forms.ModelForm):

    class Meta:
        model = Message
        fields = ['body']

class CreateRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['topic', 'name', 'description']
