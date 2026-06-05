from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


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
    def placeholder_image_source(self):
        return f'{settings.STATIC_URL.rstrip("/")}/images/property-placeholder.svg'

    def is_placeholder_url(self, image_url):
        if not image_url:
            return True

        normalized_url = image_url.strip().lower()
        placeholder_markers = (
            'via.placeholder.com',
            'property-placeholder.svg',
            'text=nincs',
            'nincs+kep',
            'nincs-kep',
            'placeholder',
        )
        return any(marker in normalized_url for marker in placeholder_markers)

    def _uploaded_image_url(self, image_field):
        if not image_field or not image_field.name:
            return None

        try:
            if image_field.storage.exists(image_field.name):
                return image_field.url
        except (OSError, ValueError):
            return None

        return None

    def _static_image_exists(self, image_url):
        static_url = settings.STATIC_URL.rstrip('/') + '/'
        if not image_url.startswith(static_url):
            return True

        static_path = image_url[len(static_url):]
        return bool(finders.find(static_path))

    def _valid_image_url(self):
        if not self.image_url or self.is_placeholder_url(self.image_url):
            return None

        if not self._static_image_exists(self.image_url):
            return None

        return self.image_url

    @property
    def first_gallery_image_source(self):
        for gallery_image in self.gallery_images.all():
            image_url = self._uploaded_image_url(gallery_image.image)
            if image_url:
                return image_url
        return None

    @property
    def display_image_url(self):
        uploaded_image_url = self._uploaded_image_url(self.image)
        if uploaded_image_url:
            return uploaded_image_url

        image_url = self._valid_image_url()
        if image_url:
            return image_url

        gallery_image_url = self.first_gallery_image_source
        if gallery_image_url:
            return gallery_image_url

        return self.placeholder_image_source

    @property
    def uses_placeholder_image(self):
        return self.display_image_url == self.placeholder_image_source

    @property
    def image_source(self):
        return self.display_image_url

    @property
    def detail_image_source(self):
        return self.display_image_url

    def __str__(self):
        return f'{self.title} - {self.location}'


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='Ingatlan',
    )
    image = models.ImageField(upload_to='properties/gallery/', verbose_name='Galériakép')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Feltöltés ideje')

    class Meta:
        ordering = ['created_at']
        verbose_name = 'Ingatlan galériakép'
        verbose_name_plural = 'Ingatlan galériaképek'

    def __str__(self):
        return f'{self.property.title} galériakép #{self.pk}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Felhasználó',
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Ingatlan',
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Hozzáadás dátuma')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'property'], name='unique_user_property_favorite'),
        ]
        ordering = ['-created_at']
        verbose_name = 'Kedvenc'
        verbose_name_plural = 'Kedvencek'

    def __str__(self):
        return f'{self.user.username} - {self.property.title}'


class ContactMessage(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_contact_messages',
        verbose_name='Küldő',
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_contact_messages',
        verbose_name='Fogadó',
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='contact_messages',
        verbose_name='Ingatlan',
    )
    message = models.TextField(verbose_name='Üzenet')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Létrehozás ideje')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Kapcsolatfelvételi üzenet'
        verbose_name_plural = 'Kapcsolatfelvételi üzenetek'

    def __str__(self):
        return f'{self.sender.username} -> {self.recipient.username}: {self.property.title}'


def delete_property_image_file(image_field):
    if image_field and image_field.name:
        image_field.storage.delete(image_field.name)


@receiver(pre_save, sender=Property)
def delete_replaced_property_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image.name and old_image.name != getattr(new_image, 'name', None):
        delete_property_image_file(old_image)


@receiver(post_delete, sender=Property)
def delete_property_image_on_delete(sender, instance, **kwargs):
    delete_property_image_file(instance.image)


@receiver(pre_save, sender=PropertyImage)
def delete_replaced_gallery_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image.name and old_image.name != getattr(new_image, 'name', None):
        delete_property_image_file(old_image)


@receiver(post_delete, sender=PropertyImage)
def delete_gallery_image_on_delete(sender, instance, **kwargs):
    delete_property_image_file(instance.image)
