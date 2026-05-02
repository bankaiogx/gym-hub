# Generated for the Review feature update.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gyms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='review',
            name='unique_review_per_user_per_gym',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='content',
            new_name='comment',
        ),
        migrations.RemoveField(
            model_name='review',
            name='title',
        ),
        migrations.RemoveField(
            model_name='review',
            name='updated_at',
        ),
        migrations.AlterField(
            model_name='review',
            name='rating',
            field=models.PositiveSmallIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]),
        ),
    ]
