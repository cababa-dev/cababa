from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField('作成日', null=False, default=timezone.now)
    updated_at = models.DateTimeField('更新日', null=False, default=timezone.now)

    class Meta:
        abstract = True