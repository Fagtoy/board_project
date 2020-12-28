from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.forms.widgets import Textarea

from .models import Bb, Rubric, Img


class ImgForm(ModelForm):
    class Meta:
        model = Img
        fields = ('desc', 'img')


class SearchRubric(forms.Form):
    keyword = forms.CharField(max_length=20, label='Искомое слово')
    rubric = forms.ModelChoiceField(queryset=Rubric.objects.all(), label='Рубрика')


class RubricForm(ModelForm):
    class Meta:
        model = Rubric
        fields = ('name',)
        widgets = {'desc': Textarea()}


class BbForm(ModelForm):
    class Meta:
        model = Bb
        fields = ('title', 'content', 'image', 'rubric', 'kind', 'price')
        labels = {'title': 'Название товара'}
        help_text = {'rubric': 'Не забудьте указать рубрику!'}


class AuthUserForm(AuthenticationForm, ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')


class RegisterUserForm(ModelForm):
    captcha = CaptchaField(label='Решите пример: ', label_suffix='',
                             error_messages={'invalid': 'Неправильно решен пример'})

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
