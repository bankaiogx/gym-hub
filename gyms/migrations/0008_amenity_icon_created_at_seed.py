from django.db import migrations, models
import django.utils.timezone


DEFAULT_AMENITIES = [
    'Free weights',
    'Cardio machines',
    'Power racks',
    '24/7 access',
    'Classes',
    'Personal training',
    'Sauna',
    'Showers',
    'Parking',
    'Women-only area',
    'Pool',
    'Boxing area',
]


def seed_default_amenities(apps, schema_editor):
    Amenity = apps.get_model('gyms', 'Amenity')
    for name in DEFAULT_AMENITIES:
        Amenity.objects.get_or_create(name=name)


def remove_seeded_amenities(apps, schema_editor):
    Amenity = apps.get_model('gyms', 'Amenity')
    Amenity.objects.filter(name__in=DEFAULT_AMENITIES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0007_alter_gym_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='amenity',
            name='icon',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='amenity',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.RunPython(seed_default_amenities, remove_seeded_amenities),
    ]
