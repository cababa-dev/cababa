import os
import uuid
import boto3

from django import forms
from django.conf import settings

from lib.spreadsheet import get_sheet


class PreRegistrationForm(forms.Form):
    AREA_KABUKI = "kabuki"
    AREA_ROPPONGI = "roppongi"
    AREA_GINZA = "ginza"
    AREA_SHIBUYA = "shibuya"
    AREA_KITASHINCHI = "kitashinchi"
    AREA_MINAMI = "minami"
    AREA_OTHER = "other"
    AREA_CHOICES = [
        (AREA_KABUKI, "歌舞伎町"),
        (AREA_ROPPONGI, "六本木"),
        (AREA_GINZA, "銀座"),
        (AREA_SHIBUYA, "渋谷"),
        (AREA_KITASHINCHI, "北新地"),
        (AREA_MINAMI, "ミナミ"),
        (AREA_OTHER, "その他"),
    ]
    STYLE_CELEB = "celeb"
    STYLE_SEXY = "sexy"
    STYLE_SLIM = "slim"
    STYLE_BUSINESS = "business"
    STYLE_YOUNG = "young"
    STYLE_SCHOOL = "school"
    STYLE_GIRL = "girl"
    STYLE_FAT = "fat"
    STYLE_CHOICES = [
        (STYLE_CELEB, "お姉さん・セレブ"),
        (STYLE_SEXY, "セクシー・ナイスバディ"),
        (STYLE_SLIM, "モデル・スレンダー"),
        (STYLE_BUSINESS, "ビジネスパーソン"),
        (STYLE_YOUNG, "ロリータ・妹"),
        (STYLE_SCHOOL, "女子大生"),
        (STYLE_GIRL, "ギャル"),
        (STYLE_FAT, "ぽっちゃり"),
    ]

    real_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '回答を入力'}))
    display_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '回答を入力'}))
    age = forms.IntegerField(required=True, widget=forms.TextInput(attrs={'placeholder': '回答を入力'}))
    line_id = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': '回答を入力'}))
    line_qrcode = forms.FileField(required=False)
    area = forms.MultipleChoiceField(choices=AREA_CHOICES, required=True)
    style = forms.ChoiceField(choices=STYLE_CHOICES, required=False)
    profile_image = forms.FileField(required=False)

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', {})
        super(PreRegistrationForm, self).__init__(*args, **kwargs)

    def upload(self, file):
        name, ext = os.path.splitext(file.name)
        filename = 'pre_register/{}{}'.format(str(uuid.uuid4()), ext)
        s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)
        bucket.put_object(Key=filename, Body=file, ACL='public-read')
        url = 'https://{0}.s3-ap-northeast-1.amazonaws.com/{1}'.format(settings.AWS_STORAGE_BUCKET_NAME, filename)
        return url

    def get_display(self, key, choices):
        for c in choices:
            if c[0] == key:
                return c[1]
        return None

    def save(self):
        request = self.context.get('request')
        data = self.cleaned_data

        # 画像データはS3に保存してURLを取得
        line_qrcode = data.get('line_qrcode')
        if line_qrcode:
            line_qrcode = self.upload(line_qrcode)
        profile_image = data.get('profile_image')
        if profile_image:
            profile_image = self.upload(profile_image)
        
        # その他データを取得
        real_name = data.get('real_name')
        display_name = data.get('display_name')
        age = data.get('age')
        line_id = data.get('line_id')
        area = data.get('area')
        style = data.get('style')

        sheet = get_sheet(settings.SPREADSHEET_KEY)
        # 現在の応募件数を取得
        num_of_records = int(sheet.acell('L1').value)

        # Google Spreadsheetに追加
        sheet.update_cell(num_of_records+2, 1, num_of_records+1)
        sheet.update_cell(num_of_records+2, 2, real_name)
        sheet.update_cell(num_of_records+2, 3, display_name)
        sheet.update_cell(num_of_records+2, 4, age)
        sheet.update_cell(num_of_records+2, 5, line_id)
        sheet.update_cell(num_of_records+2, 6, line_qrcode)
        sheet.update_cell(num_of_records+2, 7, ",".join([self.get_display(a, self.AREA_CHOICES) for a in area]))
        sheet.update_cell(num_of_records+2, 8, self.get_display(style, self.STYLE_CHOICES))
        sheet.update_cell(num_of_records+2, 9, profile_image)

        # 件数をカウントアップ
        sheet.update_cell(1, 12, num_of_records+1)