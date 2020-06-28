import datetime

from django import forms

from users.models import HostessProfile


class HostessSearchForm(forms.Form):
    AGE_CHOICES = [
        ('20-25', '20-25歳'),
        ('25-30', '25-30歳'),
        ('30-35', '30-35歳'),
        ('35-40', '35-40歳'),
        ('40-45', '40-45歳'),
        ('45-50', '45-50歳'),
    ]

    # キーワード
    keyword = forms.CharField(required=False)
    # 出勤時間
    date = forms.CharField(required=False)
    time = forms.CharField(required=False)
    # 体型
    body = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=HostessProfile.BodyTypes.choices, required=False)
    # 年齢
    age = forms.MultipleChoiceField(widget=forms.SelectMultiple, choices=AGE_CHOICES, required=False)

    def clean_age(self):
        # [start_age, end_age]のリストに変換
        age_str_list = self.cleaned_data.get('age', [])
        ages = [list(map(int, age_str.split('-'))) for age_str in age_str_list]
        return ages

    def clean(self):
        cleaned_data = self.cleaned_data
        # 出勤時間の検索範囲を整理 -> datetimeのフィールドに変換
        date_str = cleaned_data.pop('date')
        time_str = cleaned_data.pop('time')
        if date_str and not time_str:
            d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            cleaned_data['datetime_start'] = d
            cleaned_data['datetime_end'] = d + datetime.timedelta(hours=23, minutes=59, seconds=59)
        elif date_str and time_str:
            start_time = time_str.split('-')[0]
            end_time = time_str.split('-')[1]
            cleaned_data['datetime_start'] = datetime.datetime.strptime('{}T{}'.format(date_str, start_time), '%Y-%m-%dT%H-%M')
            cleaned_data['datetime_end'] = datetime.datetime.strptime('{}T{}'.format(date_str, end_time), '%Y-%m-%dT%H-%M')
        return cleaned_data