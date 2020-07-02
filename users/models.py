import uuid

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Permission
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.contrib.postgres.fields import ArrayField

from lib.models import BaseModel
from . import managers


class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()

    class UserTypes(models.TextChoices):
        GUEST = "GU", "ゲスト"
        HOSTESS = "HO", "嬢"
        STAFF = "ST", "グループスタッフ"

    user_id = models.UUIDField(_('user_id'), default=uuid.uuid4, unique=True, db_index=True)
    line_user_id = models.CharField(_('line_user_id'), max_length=100, db_index=True)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    display_name = models.CharField(_('display name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    user_type = models.CharField(_('user type'), max_length=2, choices=UserTypes.choices, default=UserTypes.GUEST, db_index=True)
    id_token = models.CharField(_('id_token'), max_length=1024, default=None, null=True)
    group = models.ForeignKey('users.Group', db_index=True, null=True, default=None, on_delete=models.CASCADE, related_name='group_staff')

    objects = managers.UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        #abstract = True

    @property
    def hostess_profile(self):
        return HostessProfile.objects.get(hostess=self)

    @property
    def guest_profile(self):
        return GuestProfile.objects.get(guest=self)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return self.display_name

    def get_short_name(self):
        return self.display_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def line_logined(self):
        if not self.hostess_profile:
            return False
        if not self.id_token:
            return False
        return True

    def __str__(self):
        return self.display_name


class HostessProfile(BaseModel, models.Model):
    class RankTypes(models.TextChoices):
        SILVER = "SR", "シルバー"
        GOLD = "GD", "ゴールド"
        PLATINUM = "PM", "プラチナ"

    class AreaTypes(models.TextChoices):
        KABUKI = "kabukicho", "歌舞伎町"
        ROPPONGI = "roppongi", "六本木"
        GINZA = "ginza", "銀座"
        SHIBUYA = "shibuya", "渋谷"
        IKEBUKURO = "ikebukuro", "池袋"
        UENO = "ueno", "上野"
        KITASHINCHI = "kitashinchi", "北新地"
        MINAMI = "minami", "ミナミ"
        NAKASU = "nakasu", "中州"
        KOKUBUNCHO = "kokubuncho", "国分町"
        SUSUKINO = "susukino", "ススキノ"
        OTHER = "other", "その他"

    class StyleTypes(models.TextChoices):
        STYLE_CELEB = "celeb", "お姉さん・セレブ"
        STYLE_SEXY = "sexy", "セクシー・ナイスバディ"
        STYLE_SLIM = "slim", "モデル・スレンダー"
        STYLE_BUSINESS = "business", "ビジネスパーソン"
        STYLE_YOUNG = "young", "ロリータ・妹"
        STYLE_SCHOOL = "school", "女子大生"
        STYLE_GIRL = "girl", "ギャル"
        STYLE_FAT = "fat", "ぽっちゃり"

    class BodyTypes(models.TextChoices):
        BODY_SLIM = "slim", "スリム"
        BODY_SEMI_SLIM = "semi-slim", "やや細目"
        BODY_NORMAL = "normal", "普通"
        BODY_GRAMMER = "glamorous", "グラマー"
        BODY_MUSCLAR = "musclar", "筋肉質"
        BODY_SEMI_FAT = "semi-fat", "ややぽっちゃり"
        BODY_FAT = "fat", "太め"

    class PersonalityTypes(models.TextChoices):
        PERSONALITY_HEAL = "heal", "癒し"
        PERSONALITY_GOODY = "goody", "天然"
        PERSONALITY_EVIL = "evil", "小悪魔"
        PERSONALITY_PURE = "pure", "ピュア/素直"
        PERSONALITY_SMART = "smart", "知的"
        PERSONALITY_GROOVY = "groovy", "ノリノリ"
        PERSONALITY_FRIENDLY = "friendly", "フレンドリー"
        PERSONALITY_OUTDOOR = "outdoor", "アウトドア"
        PERSONALITY_INDOOR = "indoor", "インドア"


    # 属性情報
    # 本名
    name = models.CharField(_('name'), max_length=100, null=True, default=None)
    # 身長
    height = models.IntegerField(_('height'), null=True, default=None, db_index=True, blank=True)
    # 出身地
    prefecture_code = models.IntegerField(_('prefecture_code'), default=-1, db_index=True)
    # キャスト経験エリア
    area = ArrayField(models.CharField(max_length=20, choices=AreaTypes.choices), db_index=True, size=10, default=list, blank=True)
    # 体型
    body = models.CharField(_('body'), max_length=20, choices=BodyTypes.choices, null=True, default=None, db_index=True, blank=True)
    # 年齢
    age = models.IntegerField(_('age'), default=None, null=True)
    # 雰囲気/スタイル
    style = ArrayField(models.CharField(max_length=20, choices=StyleTypes.choices), db_index=True, size=10, default=list, blank=True)
    # 性格
    personality = ArrayField(models.CharField(max_length=20, choices=PersonalityTypes.choices), db_index=True, size=10, default=list, blank=True)
    # メッセージ
    message = models.TextField(_('message'), null=True, default=None)
    # プロフィール画像
    images = ArrayField(models.URLField(max_length=1024), size=10, default=list)

    # 料金モデル
    rank = models.CharField(_('rank'), max_length=2, choices=RankTypes.choices, default=RankTypes.SILVER, db_index=True)

    hostess = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        primary_key=True,
    )

    objects = managers.HostessProfileManager()


class GuestProfile(BaseModel, models.Model):
    prefecture_code = models.IntegerField(_('prefecture_code'), default=-1, db_index=True)
    
    guest = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE,
        primary_key=True,
    )


class Group(BaseModel, models.Model):
    group_id = models.UUIDField(_('group_id'), default=uuid.uuid4, unique=True, db_index=True)
    name = models.CharField(_('name'), max_length=50, db_index=True, unique=True) # 英字名
    title = models.CharField(_('title'), max_length=200)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('permissions'),
        related_name='group_permissions',
        blank=True,
    )

    hostess = models.ManyToManyField(User, through='HostessGroupRelationship', related_name='group_hostess')

    objects = managers.GroupManager()

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class HostessGroupRelationship(BaseModel, models.Model):
    hostess_group_id = models.UUIDField(_('hostes_group_id'), default=uuid.uuid4, unique=True, db_index=True)
    hostess = models.ForeignKey('users.User', on_delete=models.CASCADE, db_index=True)
    group = models.ForeignKey('users.Group', on_delete=models.CASCADE, db_index=True)

    class Meta:
        unique_together = (
            ('hostess', 'group'),
        )