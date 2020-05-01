from django import forms
from django.contrib.auth import authenticate, login

from users.models import User



class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(min_length=8, required=True)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(LoginForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(username=email, user_type=User.UserTypes.STAFF).exists():
            raise forms.ValidationError('このメールアドレスは登録されていません')
        return email

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        user = authenticate(username=email, password=password)
        if not user:
            raise forms.ValidationError('メールアドレスかパスワードが間違っています')
        cleaned_data['user'] = user
        return cleaned_data

    def save(self):
        user = self.cleaned_data['user']
        request = self.context['request']
        login(request, user)
        return user