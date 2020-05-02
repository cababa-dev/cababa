from django import forms
from django.contrib.auth import authenticate, login

from users.models import User, Group



class LoginForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(min_length=6, required=True)

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


class SignupForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(min_length=8, required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    group_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(SignupForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('このメールアドレスはすでに登録されています')
        return email

    def clean_group_name(self):
        group_name = self.cleaned_data.get('group_name')
        if Group.objects.filter(name=group_name).exists():
            raise forms.ValidationError('この名前はすでに登録されています')
        return group_name
    
    def save(self):
        data = self.cleaned_data
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        group_name = data.get('group_name')

        group = Group.objects.create(name=group_name, title="")
        user = User.objects.create(
            username=email,
            email=email,
            group=group,
            first_name=first_name,
            last_name=last_name,
            user_type=User.UserTypes.STAFF
        )
        user.set_password(password)
        user.save()
        return user