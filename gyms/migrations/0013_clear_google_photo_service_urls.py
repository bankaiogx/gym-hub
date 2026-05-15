from django.db import migrations


BROKEN_GOOGLE_PHOTO_PATH = '/maps/api/place/js/PhotoService.GetPhoto'


def clear_broken_google_photo_urls(apps, schema_editor):
    Gym = apps.get_model('gyms', 'Gym')
    Gym.objects.filter(image_url__contains=BROKEN_GOOGLE_PHOTO_PATH).update(image_url='')


def restore_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0012_alter_gym_image'),
    ]

    operations = [
        migrations.RunPython(clear_broken_google_photo_urls, restore_noop),
    ]
