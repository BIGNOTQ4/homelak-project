from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Cím')),
                ('location', models.CharField(max_length=200, verbose_name='Település')),
                ('price', models.IntegerField(verbose_name='Ár (Ft)')),
                ('sq_meter', models.IntegerField(verbose_name='Alapterület (m²)')),
                ('rooms', models.IntegerField(verbose_name='Szobák száma')),
                ('description', models.TextField(verbose_name='Leírás')),
                ('image_url', models.URLField(blank=True, verbose_name='Kép URL')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
