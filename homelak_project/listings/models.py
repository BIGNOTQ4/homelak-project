from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Property(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='properties',
        verbose_name='Feltöltő',
    )
    title = models.CharField(max_length=200, verbose_name='Cím')
    location = models.CharField(max_length=200, verbose_name='Település')
    price = models.IntegerField(
        verbose_name='Ár (Ft)',
        validators=[MinValueValidator(1, message='Az ár csak 1 vagy annál nagyobb lehet.')],
    )
    sq_meter = models.IntegerField(
        verbose_name='Alapterület (m²)',
        validators=[MinValueValidator(1, message='Az alapterület csak 1 vagy annál nagyobb lehet.')],
    )
    rooms = models.IntegerField(
        verbose_name='Szobák száma',
        validators=[MinValueValidator(1, message='A szobák száma csak 1 vagy annál nagyobb lehet.')],
    )
    description = models.TextField(verbose_name='Leírás')
    image_url = models.URLField(blank=True, verbose_name='Kép URL')
    image = models.ImageField(
        upload_to='properties/',
        blank=True,
        null=True,
        verbose_name='Feltöltött kép',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=models.Q(price__gte=1), name='property_price_gte_1'),
            models.CheckConstraint(condition=models.Q(sq_meter__gte=1), name='property_sq_meter_gte_1'),
            models.CheckConstraint(condition=models.Q(rooms__gte=1), name='property_rooms_gte_1'),
        ]

    @property
    def image_source(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://via.placeholder.com/300x200?text=Nincs+kep'

    @property
    def detail_image_source(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return 'https://via.placeholder.com/1000x600?text=Nincs+kep'

    def __str__(self):
        return f'{self.title} - {self.location}'
