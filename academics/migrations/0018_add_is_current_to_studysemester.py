from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academics', '0017_alter_programme_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='studysemester',
            name='is_current',
            field=models.BooleanField(default=False),
        ),
    ]
