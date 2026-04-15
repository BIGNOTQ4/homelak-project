from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0002_property_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='properties/', verbose_name='Feltöltött kép'),
        ),
    ]
