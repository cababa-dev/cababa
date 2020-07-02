import os
import uuid
import datetime

from django import forms
from django.core.files.storage import default_storage
from django.conf import settings

from lib import line
from users.models import GuestProfile



class SignupForm(forms.Form):
    display_name = forms.CharField(max_length=100)
    prefecture_code = forms.IntegerField(required=False)
    
    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        super(SignupForm, self).__init__(*args, **kwargs)
    
    def clean_prefecture_code(self):
        prefecture_code = self.cleaned_data['prefecture_code']
        if prefecture_code < 0 or prefecture_code > 47:
            raise forms.ValidationError('不正な値です')
        return prefecture_code
    
    def clean(self):
        cleaned_data = self.cleaned_data
        # LINE@に登録しているかどうかチェック
        user = self.context['request'].user
        if not line.registered_line_at(user.id_token, is_guest=True):
            raise forms.ValidationError('LINE@を友達に追加してください')
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        display_name = data['display_name']
        prefecture_code = data['prefecture_code']
        # プロフィールの作成
        guest = self.context['request'].user
        guest.display_name = display_name
        guest.save()
        guest_profile = GuestProfile.objects.create(
            guest=guest,
            prefecture_code=prefecture_code,
        )
        return guest_profile