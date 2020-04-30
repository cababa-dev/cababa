# Generated by Django 3.0.5 on 2020-04-26 12:04

from django.conf import settings
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import users.managers
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('user_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True, verbose_name='user_id')),
                ('line_user_id', models.CharField(db_index=True, max_length=100, verbose_name='line_user_id')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('display_name', models.CharField(blank=True, max_length=150, verbose_name='display name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('user_type', models.CharField(choices=[('GU', 'ゲスト'), ('HO', '嬢'), ('ST', 'グループスタッフ')], db_index=True, default='GU', max_length=2, verbose_name='user type')),
                ('id_token', models.CharField(default=None, max_length=1024, null=True, verbose_name='id_token')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', users.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('group_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True, verbose_name='group_id')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='name')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
            managers=[
                ('objects', users.managers.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name='HostesTagRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('hostes_tag_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True, verbose_name='hostes_tag_id')),
                ('hostes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TagGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('tag_group_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True, verbose_name='tag_group_id')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='name')),
                ('title', models.CharField(max_length=100, verbose_name='title')),
                ('description', models.TextField(default=None, null=True, verbose_name='description')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GuestProfile',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('prefecture_code', models.IntegerField(db_index=True, default=-1, verbose_name='prefecture_code')),
                ('guest', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HostessProfile',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('image', models.URLField(max_length=1024, verbose_name='image')),
                ('birthday', models.DateField(db_index=True, default=None, null=True, verbose_name='birthday')),
                ('prefecture_code', models.IntegerField(db_index=True, default=-1, verbose_name='prefecture_code')),
                ('height', models.IntegerField(db_index=True, default=None, null=True, verbose_name='height')),
                ('hostess', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('tag_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True, verbose_name='tag_id')),
                ('name', models.CharField(db_index=True, max_length=50, unique=True, verbose_name='name')),
                ('value', models.CharField(max_length=100, verbose_name='value')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.TagGroup')),
                ('hostes', models.ManyToManyField(through='users.HostesTagRelationship', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='hostestagrelationship',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Tag'),
        ),
        migrations.CreateModel(
            name='HostesGroupRelationship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='作成日')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='更新日')),
                ('hostes_group_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True, verbose_name='hostes_group_id')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Group')),
                ('hostes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('hostes', 'group')},
            },
        ),
        migrations.AddField(
            model_name='group',
            name='hostes',
            field=models.ManyToManyField(through='users.HostesGroupRelationship', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(blank=True, related_name='group_permissions', to='auth.Permission', verbose_name='permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='hostestagrelationship',
            unique_together={('hostes', 'tag')},
        ),
    ]
