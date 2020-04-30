import xlrd, xlwt

from . import models


class TagService:
    def import_tags(self, filepath):
        wb = xlrd.open_workbook(filepath)
        sheet = wb.sheet_by_name('tags')
        tag_groups = dict()
        # ignore header
        for row in range(1, sheet.nrows-1):
            cols = sheet.row_values(row)
            group_name = cols[0]
            group_title = cols[1]
            tag_name = cols[2]
            tag_value = cols[3]
            if not tag_groups.get(group_name):
                tag_groups[group_name] = {'title': group_title, 'tags': []}
            tag_groups[group_name]['tags'].append(dict(name=tag_name, value=tag_value))
        for name, group in tag_groups.items():
            tag_group, created = models.TagGroup.objects.get_or_create(name=name, title=group['title'])
            for tag_data in group['tags']:
                tag, created = models.Tag.objects.get_or_create(name=tag_data['name'], value=tag_data['value'], group=tag_group)


class HostessService:
    def generate_dummy_hostess(self, count=100):
        # ダミーデータ生成
        import uuid
        from random import randint
        from faker import Faker
        import japanmap

        fake = Faker(['ja-JP'])
        dummy_images = [
            'https://dllbcrkkow3pj.cloudfront.net/image/300x300/33be5aa4953abf86930953cb6dafed7f.jpg',
            'https://dllbcrkkow3pj.cloudfront.net/image/300x300/12675f380316946b984bf92e079a0b6e.jpg',
            'https://storage.googleapis.com/luline/cast/6/6856/other_th_56a29ce2ba616e442b89c9067d04af1b.jpg',
            'https://img.fankura.com/img/t1w350h350/A7/cH/A7cHMB1mR6B3_4_233788.jpg',
            'https://img.fankura.com/img/t1w350h350cv1/Uo/zO/UozOOgp77fFH_4_586395.jpg',
            'https://img.fankura.com/img/t1w350h350/QU/g6/QUg6QU7YiHvA_4_297348.jpg',
        ]
        styles = models.Tag.objects.filter(group=models.TagGroup.objects.get(name='style'))
        personalities = models.Tag.objects.filter(group=models.TagGroup.objects.get(name='personality'))
        faces = models.Tag.objects.filter(group=models.TagGroup.objects.get(name='face'))

        for _ in range(count):
            name = fake.last_name_female() + fake.first_name_female()
            image = dummy_images[randint(0, len(dummy_images)-1)]
            birthday = fake.date_of_birth()
            prefecture_code = japanmap.pref_code(fake.prefecture())
            height = randint(140, 180)
            style = styles[randint(0, len(styles)-1)]
            personality = personalities[randint(0, len(personalities)-1)]
            face = faces[randint(0, len(faces)-1)]

            hostes = models.User.objects.create(user_type=models.User.UserTypes.HOSTESS, username=str(uuid.uuid4()), display_name=name)
            profile = models.HostessProfile.objects.create(
                hostes=hostes,
                image=image,
                birthday=birthday,
                prefecture_code=prefecture_code,
                height=height,
            )