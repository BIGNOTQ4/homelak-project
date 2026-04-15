from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('listings', '0003_property_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='price',
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1, message='Az ár csak 1 vagy annál nagyobb lehet.')],
                verbose_name='Ár (Ft)',
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='sq_meter',
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1, message='Az alapterület csak 1 vagy annál nagyobb lehet.')],
                verbose_name='Alapterület (m²)',
            ),
        ),
        migrations.AlterField(
            model_name='property',
            name='rooms',
            field=models.IntegerField(
                validators=[django.core.validators.MinValueValidator(1, message='A szobák száma csak 1 vagy annál nagyobb lehet.')],
                verbose_name='Szobák száma',
            ),
        ),
        migrations.AddConstraint(
            model_name='property',
            constraint=models.CheckConstraint(condition=models.Q(('price__gte', 1)), name='property_price_gte_1'),
        ),
        migrations.AddConstraint(
            model_name='property',
            constraint=models.CheckConstraint(condition=models.Q(('sq_meter__gte', 1)), name='property_sq_meter_gte_1'),
        ),
        migrations.AddConstraint(
            model_name='property',
            constraint=models.CheckConstraint(condition=models.Q(('rooms__gte', 1)), name='property_rooms_gte_1'),
        ),
    ]
