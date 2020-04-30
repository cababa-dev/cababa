import os
import uuid
import datetime

from django import forms
from django.core.files.storage import default_storage
from django.conf import settings

from lib import line
from users.models import HostessProfile, TagGroup, Tag


upload_dir = os.path.join(settings.MEDIA_ROOT, 'hostess/profile_image/')

class SignupForm(forms.Form):
    display_name = forms.CharField(max_length=100)
    image = forms.FileField()
    birthday = forms.CharField(required=False)
    prefecture_code = forms.IntegerField(required=False)
    height = forms.IntegerField(required=False)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(SignupForm, self).__init__(*args, **kwargs)

    def clean_birthday(self):
        birthday_str = self.cleaned_data['birthday']
        if not birthday_str:
            return None
        try:
            birthday = datetime.datetime.strptime(birthday_str, '%Y-%m-%d').date()
        except ValueError:
            raise forms.ValidationError('不正な形式です')
        return birthday
    
    def clean_prefecture_code(self):
        prefecture_code = self.cleaned_data['prefecture_code']
        if prefecture_code < 0 or prefecture_code > 47:
            raise forms.ValidationError('不正な値です')
        return prefecture_code
    
    def clean_image(self):
        image_file = self.cleaned_data['image']
        filename = image_file.name.split('.')
        filename[0] = str(uuid.uuid4())
        filename = '.'.join(filename)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        filename = default_storage.save('hostess/profile_image/'+filename, image_file)
        image_url = default_storage.url(filename)
        return image_url

    def clean(self):
        cleaned_data = self.cleaned_data
        # LINE@に登録しているかどうかチェック
        user = self.context['request'].user
        if not line.registered_line_at(user.id_token, is_guest=False):
            raise forms.ValidationError('LINE@を友達に追加してください')
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        display_name = data['display_name']
        image = data['image']
        birthday = data['birthday']
        prefecture_code = data['prefecture_code']
        height = data['height']
        # プロフィールの作成
        hostess = self.context['request'].user
        hostess.display_name = display_name
        hostess.save()
        hostess_profile = HostessProfile.objects.create(
            hostess=hostess,
            image=image,
            birthday=birthday,
            prefecture_code=prefecture_code,
            height=height,
        )
        return hostess_profile