import os
import uuid

from django import forms
from django.contrib.auth import authenticate, login
from django.core.files.storage import default_storage
from django.conf import settings

from users.models import User, Group, HostessProfile
from . import models


upload_dir = os.path.join(settings.MEDIA_ROOT, 'hostess/profile_image/')


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


class SignupConfirmForm(forms.Form):
    otp_id = forms.UUIDField(required=True)
    password1 = forms.CharField(min_length=8, required=True)
    password2 = forms.CharField(min_length=8, required=True)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(SignupConfirmForm, self).__init__(*args, **kwargs)

    def clean_otp_id(self):
        otp_id = self.cleaned_data.get('otp_id')
        try:
            otp = models.OTP.objects.get(otp_id=otp_id)
        except models.OTP.DoesNotError:
            raise forms.ValidationError('このOTPは存在しません')
        return otp

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('同じパスワードを入力してください')

    def save(self):
        otp = self.cleaned_data['otp_id']
        password = self.cleaned_data['password1']
        user = otp.user
        user.set_password(password)
        user.save()
        return user


class StaffForm(forms.Form):
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(StaffForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError('このメールアドレスはすでに登録されています')
        return email
    
    def create(self):
        data = self.cleaned_data
        email = data.get('email')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        group = self.context['request'].user.group
        user = User.objects.create(
            username=email,
            email=email,
            group=group,
            first_name=first_name,
            last_name=last_name,
            user_type=User.UserTypes.STAFF
        )
        user.save()
        otp = models.OTP.objects.create(user=user)
        return otp
    
    def update(self):
        data = self.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        user = self.context['staff']
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user


class StaffEditMeForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(StaffEditMeForm, self).__init__(*args, **kwargs)
    
    def update(self):
        data = self.cleaned_data
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        user = self.context['request'].user
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user


class HostessForm(forms.ModelForm):
    display_name = forms.CharField()
    profile_image1 = forms.FileField()
    profile_image2 = forms.FileField(required=False)
    profile_image3 = forms.FileField(required=False)
    profile_image4 = forms.FileField(required=False)

    area = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.AreaTypes.choices, required=False)
    style = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.StyleTypes.choices, required=False)
    personality = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.PersonalityTypes.choices, required=False)

    line_id = forms.CharField()

    class Meta:
        model = HostessProfile
        fields = ('name', 'height', 'prefecture_code', 'body', 'age', 'message', 'rank',)
    
    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(HostessForm, self).__init__(*args, **kwargs)
    
    def upload(self, image_file):
        filename = image_file.name.split('.')
        filename[0] = str(uuid.uuid4())
        filename = '.'.join(filename)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        filename = default_storage.save('hostess/profile_image/'+filename, image_file)
        image_url = default_storage.url(filename)
        image_url = image_url.split('?')[0]
        return image_url

    def create(self):
        data = self.cleaned_data

        # ホステスを作成
        # 登録したグループ情報を保存
        user = User.objects.create(
            username=str(uuid.uuid4()),
            display_name=data['display_name'],
            group=self.context['request'].user.group,
            line_user_id=data['line_id'],
            user_type=User.UserTypes.HOSTESS,
        )
        # プロフィールを作成
        hostess_profile = HostessProfile(
            hostess=user,
            name=data['name'],
            height=data['height'],
            prefecture_code=data['prefecture_code'],
            area=data['area'],
            body=data['body'],
            age=data['age'],
            style=data['style'],
            personality=data['personality'],
            message=data['message'],
            rank=data['rank'],
        )
        # 画像アップロード
        profile_images = []
        if data.get('profile_image1'):
            profile_images.append(self.upload(data.get('profile_image1')))
        if data.get('profile_image2'):
            profile_images.append(self.upload(data.get('profile_image2')))
        if data.get('profile_image3'):
            profile_images.append(self.upload(data.get('profile_image3')))
        if data.get('profile_image4'):
            profile_images.append(self.upload(data.get('profile_image4')))
        hostess_profile.images = profile_images
        hostess_profile.save()
        
        return hostess_profile