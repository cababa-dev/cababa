import os
import uuid
import datetime

from django import forms
from django.core.files.storage import default_storage
from django.conf import settings

from lib import line
from users.models import HostessProfile


upload_dir = os.path.join(settings.MEDIA_ROOT, 'hostess/profile_image/')


class SignupForm(forms.Form):
    # 名前(本名)
    name = forms.CharField()
    # 名前(源氏名)
    display_name = forms.CharField()
    # 身長
    height = forms.IntegerField(required=False)
    # 年齢
    age = forms.IntegerField()
    # 画像
    profile_image1 = forms.FileField()
    profile_image2 = forms.FileField(required=False)
    profile_image3 = forms.FileField(required=False)
    profile_image4 = forms.FileField(required=False)
    # 出身地
    prefecture_code = forms.IntegerField()
    # 体型
    body = forms.ChoiceField(choices=HostessProfile.BodyTypes.choices)
    # キャスト経験エリア
    area = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.AreaTypes.choices, required=False)
    # 雰囲気/スタイル
    style = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.StyleTypes.choices, required=False)
    # 性格
    personality = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.PersonalityTypes.choices, required=False)
    # 一言メッセージ
    message = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(SignupForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        # LINE@に登録しているかどうかチェック
        user = self.context['request'].user
        if not line.registered_line_at(user.id_token, is_guest=False):
            raise forms.ValidationError('LINE@を友達に追加してください')
        return cleaned_data

    def upload(self, image_file):
        filename = image_file.name.split('.')
        filename[0] = str(uuid.uuid4())
        filename = '.'.join(filename)
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        filename = default_storage.save('hostess/profile_image/'+filename, image_file)
        image_url = default_storage.url(filename)
        # アクセストークンを削除
        image_url = image_url.split('?')[0]
        return image_url

    def save(self):
        data = self.cleaned_data
        user = self.context['request'].user
        profile, created = HostessProfile.objects.get_or_create(hostess=user)

        # 画像のアップロード
        images = []
        image1 = data.get('profile_image1')
        if image1:
            image1_url = self.upload(image1)
            images.append(image1_url)
        image2 = data.get('profile_image2')
        if image2:
            image2_url = self.upload(image2)
            images.append(image2_url)
        image3 = data.get('profile_image3')
        if image3:
            image3_url = self.upload(image3)
            images.append(image3_url)
        image4 = data.get('profile_image4')
        if image4:
            image4_url = self.upload(image4)
            images.append(image4_url)

        # プロフィールの設定と保存
        profile.name = data.get('name')
        profile.height = data.get('height')
        profile.age = data.get('age')
        profile.images = images
        profile.prefecture_code = data.get('prefecture_code')
        profile.body = data.get('body')
        profile.area = data.get('area')
        profile.style = data.get('style')
        profile.personality = data.get('personality')
        profile.message = data.get('message')
        profile.save()

        # 表示名はuserモデルに保存
        user.display_name = data.get('display_name')
        user.save()
