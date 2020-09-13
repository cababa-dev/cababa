import datetime
from django.utils.timezone import localtime

def get_display_dt(dt):
    # 6時以前の場合は前の日とする
    if localtime(dt).hour < 6:
        return localtime(dt) - datetime.timedelta(days=1)
    else:
        return localtime(dt)