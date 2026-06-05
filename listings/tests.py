import io
import os
import shutil
import tempfile

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.template import Context, Template
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .forms import PropertyForm
from .models import ContactMessage, Favorite, Property, PropertyImage


def create_user(username='tesztuser'):
    return User.objects.create_user(username=username, password='StrongPass123')


def property_data(**overrides):
    data = {
        'title': 'Teszt lakas',
        'location': 'Budapest',
        'price': 50000000,
        'sq_meter': 65,
        'rooms': 3,
        'description': 'Vilagos, jo allapotu ingatlan.',
        'image_url': '',
    }
    data.update(overrides)
    return data


def create_property(owner=None, **overrides):
    return Property.objects.create(owner=owner, **property_data(**overrides))


def test_image_file(name='test.png', image_format='PNG', content_type='image/png'):
    image_bytes = io.BytesIO()
    Image.new('RGB', (10, 10), color='white').save(image_bytes, format=image_format)
    return SimpleUploadedFile(name, image_bytes.getvalue(), content_type=content_type)


def oversized_png_file():
    image_bytes = io.BytesIO()
    image = Image.frombytes('RGB', (1500, 1500), os.urandom(1500 * 1500 * 3))
    image.save(image_bytes, format='PNG')
    return SimpleUploadedFile('large.png', image_bytes.getvalue(), content_type='image/png')


class PropertyModelValidationTests(TestCase):
    def test_price_must_be_positive(self):
        for value in [0, -1]:
            with self.subTest(price=value):
                property_obj = Property(**property_data(price=value))

                with self.assertRaises(ValidationError):
                    property_obj.full_clean()


class PropertyImageValidationTests(TestCase):
    def test_form_accepts_valid_image_upload(self):
        form = PropertyForm(data=property_data(), files={'image': test_image_file()})

        self.assertTrue(form.is_valid(), form.errors)

    def test_form_rejects_oversized_image_upload(self):
        form = PropertyForm(data=property_data(), files={'image': oversized_png_file()})

        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)
        self.assertIn('legfeljebb 5 MB', form.errors['image'][0])

    def test_form_rejects_unsupported_image_extension(self):
        form = PropertyForm(
            data=property_data(),
            files={'image': test_image_file(name='test.bmp', content_type='image/bmp')},
        )

        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_form_rejects_non_image_upload(self):
        text_file = SimpleUploadedFile(
            'not-image.jpg',
            b'nem kep fajl',
            content_type='image/jpeg',
        )

        form = PropertyForm(data=property_data(), files={'image': text_file})

        self.assertFalse(form.is_valid())
        self.assertIn('image', form.errors)

    def test_form_accepts_multiple_gallery_images(self):
        form = PropertyForm(
            data=property_data(),
            files={
                'gallery_images': [
                    test_image_file(name='gallery-1.png'),
                    test_image_file(name='gallery-2.png'),
                ],
            },
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(len(form.cleaned_data['gallery_images']), 2)

    def test_form_rejects_invalid_gallery_image(self):
        text_file = SimpleUploadedFile(
            'not-image.jpg',
            b'nem kep fajl',
            content_type='image/jpeg',
        )
        form = PropertyForm(data=property_data(), files={'gallery_images': [text_file]})

        self.assertFalse(form.is_valid())
        self.assertIn('gallery_images', form.errors)


class PropertyImageCleanupTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_replaced_property_image_file_is_deleted(self):
        property_obj = create_property(image=test_image_file(name='first.png'))
        old_image_path = property_obj.image.path
        self.assertTrue(property_obj.image.storage.exists(property_obj.image.name))

        property_obj.image = test_image_file(name='second.png')
        property_obj.save()

        self.assertFalse(property_obj.image.storage.exists('properties/first.png'))
        self.assertFalse(os.path.exists(old_image_path))
        self.assertTrue(property_obj.image.storage.exists(property_obj.image.name))

    def test_property_image_file_is_deleted_when_property_is_deleted(self):
        property_obj = create_property(image=test_image_file(name='delete-me.png'))
        image_name = property_obj.image.name
        self.assertTrue(property_obj.image.storage.exists(image_name))

        property_obj.delete()

        self.assertFalse(property_obj.image.storage.exists(image_name))

    def test_gallery_image_file_is_deleted_when_gallery_image_is_deleted(self):
        property_obj = create_property()
        gallery_image = PropertyImage.objects.create(
            property=property_obj,
            image=test_image_file(name='gallery-delete.png'),
        )
        image_name = gallery_image.image.name
        self.assertTrue(gallery_image.image.storage.exists(image_name))

        gallery_image.delete()

        self.assertFalse(gallery_image.image.storage.exists(image_name))

    def test_gallery_image_file_is_deleted_when_property_is_deleted(self):
        property_obj = create_property()
        gallery_image = PropertyImage.objects.create(
            property=property_obj,
            image=test_image_file(name='gallery-property-delete.png'),
        )
        image_name = gallery_image.image.name
        self.assertTrue(gallery_image.image.storage.exists(image_name))

        property_obj.delete()

        self.assertFalse(gallery_image.image.storage.exists(image_name))

    def test_sq_meter_must_be_positive(self):
        for value in [0, -1]:
            with self.subTest(sq_meter=value):
                property_obj = Property(**property_data(sq_meter=value))

                with self.assertRaises(ValidationError):
                    property_obj.full_clean()

    def test_rooms_must_be_positive(self):
        for value in [0, -1]:
            with self.subTest(rooms=value):
                property_obj = Property(**property_data(rooms=value))

                with self.assertRaises(ValidationError):
                    property_obj.full_clean()


class PropertyImageSourceTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_display_image_url_uses_first_gallery_image_when_main_image_and_url_are_missing(self):
        property_obj = create_property(image_url='')
        gallery_image = PropertyImage.objects.create(
            property=property_obj,
            image=test_image_file(name='gallery-fallback.jpg', image_format='JPEG', content_type='image/jpeg'),
        )

        self.assertEqual(property_obj.display_image_url, gallery_image.image.url)

    def test_display_image_url_uses_image_url_before_gallery_image(self):
        property_obj = create_property(image_url='/static/images/demo_properties/budapest-premium-lakas.jpg')
        PropertyImage.objects.create(
            property=property_obj,
            image=test_image_file(name='gallery-fallback.jpg', image_format='JPEG', content_type='image/jpeg'),
        )

        self.assertEqual(property_obj.display_image_url, '/static/images/demo_properties/budapest-premium-lakas.jpg')

    def test_display_image_url_uses_local_placeholder_as_final_fallback(self):
        property_obj = create_property(image_url='')
        property_obj.image.name = 'properties/missing-file.jpg'

        self.assertEqual(property_obj.display_image_url, f'{settings.STATIC_URL.rstrip("/")}/images/property-placeholder.svg')
        self.assertTrue(property_obj.uses_placeholder_image)


class SeedDemoPropertiesCommandTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_seed_command_creates_realistic_properties_with_images(self):
        call_command('seed_demo_properties', reset=True, verbosity=0)

        properties = Property.objects.filter(owner__username='homelak_demo')

        self.assertEqual(properties.count(), 10)
        self.assertTrue(all(property_obj.price >= 30000000 for property_obj in properties))
        self.assertTrue({'Budapest', 'Debrecen', 'Győr', 'Szeged', 'Pécs'}.issubset(
            set(properties.values_list('location', flat=True))
        ))
        self.assertTrue(all(property_obj.image_url for property_obj in properties))
        self.assertTrue(all('/static/images/demo_properties/' in property_obj.image_url for property_obj in properties))
        self.assertFalse(any('placeholder' in property_obj.display_image_url for property_obj in properties))
        self.assertGreaterEqual(len({property_obj.display_image_url for property_obj in properties}), 8)
        self.assertFalse(any(property_obj.image for property_obj in properties))
        self.assertEqual(PropertyImage.objects.filter(property__in=properties).count(), 0)

    def test_seed_command_repairs_legacy_homelak_sample_image(self):
        legacy_property = create_property(
            owner=None,
            title='Kertes sorházi lakás',
            location='Győr',
            price=68900000,
            image_url='https://static.ezermester.hu/Ezermester-print/2021/12/sorhazak/1.jpg',
        )

        call_command('seed_demo_properties', reset=True, verbosity=0)

        legacy_property.refresh_from_db()
        self.assertTrue(Property.objects.filter(pk=legacy_property.pk).exists())
        self.assertEqual(legacy_property.image_url, '/static/images/demo_properties/gyor-csaladi-haz.jpg')
        self.assertEqual(legacy_property.display_image_url, '/static/images/demo_properties/gyor-csaladi-haz.jpg')
        self.assertFalse(legacy_property.uses_placeholder_image)

    def test_seed_command_repairs_legacy_homelak_sample_detail_image(self):
        legacy_property = create_property(
            owner=None,
            title='Családi ház kerttel',
            location='Debrecen',
            price=74900000,
            image_url='',
        )

        call_command('seed_demo_properties', reset=True, verbosity=0)
        legacy_property.refresh_from_db()
        response = self.client.get(reverse('property_detail', args=[legacy_property.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'src="/static/images/demo_properties/debrecen-csaladi-otthon.jpg"',
        )
        self.assertNotContains(response, 'src="/static/images/property-placeholder.svg"')


class TemplateFilterTests(TestCase):
    def test_format_price_uses_hungarian_grouping(self):
        template = Template('{% load property_extras %}{{ price|format_price }} Ft')

        rendered = template.render(Context({'price': 41900000}))

        self.assertEqual(rendered, '41 900 000 Ft')


class PropertyPermissionTests(TestCase):
    def setUp(self):
        self.owner = create_user('owner')
        self.other_user = create_user('other')
        self.property = create_property(owner=self.owner)

    def test_other_user_cannot_open_edit_page(self):
        self.client.login(username='other', password='StrongPass123')

        response = self.client.get(reverse('edit_property', args=[self.property.pk]))

        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_edit_property(self):
        self.client.login(username='other', password='StrongPass123')

        response = self.client.post(
            reverse('edit_property', args=[self.property.pk]),
            property_data(title='Jogtalan modositas'),
        )

        self.assertEqual(response.status_code, 404)
        self.property.refresh_from_db()
        self.assertEqual(self.property.title, 'Teszt lakas')

    def test_other_user_cannot_open_delete_page(self):
        self.client.login(username='other', password='StrongPass123')

        response = self.client.get(reverse('delete_property', args=[self.property.pk]))

        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_property(self):
        self.client.login(username='other', password='StrongPass123')

        response = self.client.post(reverse('delete_property', args=[self.property.pk]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(Property.objects.filter(pk=self.property.pk).exists())


class PropertyCrudTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.user = create_user('cruduser')
        self.client.login(username='cruduser', password='StrongPass123')

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_authenticated_user_can_create_property(self):
        response = self.client.post(reverse('create_property'), property_data())

        property_obj = Property.objects.get()
        self.assertRedirects(response, reverse('property_detail', args=[property_obj.pk]))
        self.assertEqual(property_obj.owner, self.user)
        self.assertEqual(property_obj.title, 'Teszt lakas')

    def test_owner_can_edit_property(self):
        property_obj = create_property(owner=self.user)

        response = self.client.post(
            reverse('edit_property', args=[property_obj.pk]),
            property_data(title='Felujitott csaladi haz', price=62000000),
        )

        self.assertRedirects(response, reverse('property_detail', args=[property_obj.pk]))
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.title, 'Felujitott csaladi haz')
        self.assertEqual(property_obj.price, 62000000)
        self.assertEqual(property_obj.owner, self.user)

    def test_owner_can_delete_property(self):
        property_obj = create_property(owner=self.user)

        response = self.client.post(reverse('delete_property', args=[property_obj.pk]))

        self.assertRedirects(response, reverse('profile'))
        self.assertFalse(Property.objects.filter(pk=property_obj.pk).exists())

    def test_authenticated_user_can_create_property_with_gallery_images(self):
        response = self.client.post(
            reverse('create_property'),
            {
                **property_data(),
                'gallery_images': [
                    test_image_file(name='create-gallery-1.png'),
                    test_image_file(name='create-gallery-2.png'),
                ],
            },
        )

        property_obj = Property.objects.get()
        self.assertRedirects(response, reverse('property_detail', args=[property_obj.pk]))
        self.assertEqual(property_obj.gallery_images.count(), 2)

    def test_owner_can_add_gallery_images_when_editing_property(self):
        property_obj = create_property(owner=self.user)

        response = self.client.post(
            reverse('edit_property', args=[property_obj.pk]),
            {
                **property_data(title='Galeriaval bovult hirdetes'),
                'gallery_images': [test_image_file(name='edit-gallery.png')],
            },
        )

        self.assertRedirects(response, reverse('property_detail', args=[property_obj.pk]))
        property_obj.refresh_from_db()
        self.assertEqual(property_obj.title, 'Galeriaval bovult hirdetes')
        self.assertEqual(property_obj.gallery_images.count(), 1)

    def test_owner_can_delete_gallery_images_when_editing_property(self):
        property_obj = create_property(owner=self.user)
        gallery_image = PropertyImage.objects.create(
            property=property_obj,
            image=test_image_file(name='remove-gallery.png'),
        )

        response = self.client.post(
            reverse('edit_property', args=[property_obj.pk]),
            {
                **property_data(),
                'delete_gallery_images': [str(gallery_image.pk)],
            },
        )

        self.assertRedirects(response, reverse('property_detail', args=[property_obj.pk]))
        self.assertFalse(PropertyImage.objects.filter(pk=gallery_image.pk).exists())

    def test_property_detail_shows_gallery_images(self):
        property_obj = create_property(owner=self.user)
        PropertyImage.objects.create(
            property=property_obj,
            image=test_image_file(name='detail-gallery.png'),
        )

        response = self.client.get(reverse('property_detail', args=[property_obj.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['gallery_images']), list(property_obj.gallery_images.all()))
        self.assertContains(response, 'Galéria')


class PropertyListFilterTests(TestCase):
    def setUp(self):
        self.budapest_property = create_property(
            title='Budapesti lakas',
            location='Budapest',
            price=55000000,
        )
        self.debrecen_property = create_property(
            title='Debreceni haz',
            location='Debrecen',
            price=42000000,
        )
        self.expensive_property = create_property(
            title='Budai villa',
            location='Budapest',
            price=120000000,
        )

    def test_list_can_be_filtered_by_location(self):
        response = self.client.get(reverse('listings'), {'location': 'Debrecen'})

        self.assertEqual(response.status_code, 200)
        properties = list(response.context['properties'])
        self.assertEqual(properties, [self.debrecen_property])

    def test_list_can_be_filtered_by_min_price(self):
        response = self.client.get(reverse('listings'), {'min_price': '60000000'})

        self.assertEqual(response.status_code, 200)
        properties = list(response.context['properties'])
        self.assertEqual(properties, [self.expensive_property])

    def test_list_can_be_filtered_by_location_and_min_price(self):
        response = self.client.get(
            reverse('listings'),
            {'location': 'Budapest', 'min_price': '60000000'},
        )

        self.assertEqual(response.status_code, 200)
        properties = list(response.context['properties'])
        self.assertEqual(properties, [self.expensive_property])


class PropertyPaginationTests(TestCase):
    def test_list_shows_six_properties_per_page(self):
        for index in range(7):
            create_property(title=f'Teszt ingatlan {index}')

        response = self.client.get(reverse('listings'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['properties']), 6)
        self.assertTrue(response.context['page_obj'].has_next())
        self.assertEqual(response.context['paginator'].count, 7)

    def test_pagination_keeps_filter_and_sort_query_params(self):
        for index in range(7):
            create_property(
                title=f'Budapesti ingatlan {index}',
                location='Budapest',
                price=40000000 + index,
            )

        response = self.client.get(
            reverse('listings'),
            {
                'location': 'Budapest',
                'min_price': '40000000',
                'sort': 'price_asc',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context['page_querystring'],
            'location=Budapest&min_price=40000000&sort=price_asc',
        )
        self.assertContains(
            response,
            '?location=Budapest&amp;min_price=40000000&amp;sort=price_asc&amp;page=2',
        )


class ProfileDashboardTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_root)
        self.override.enable()
        self.user = create_user('dashboarduser')
        self.sender = create_user('dashboardsender')
        self.client.login(username='dashboarduser', password='StrongPass123')

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_profile_dashboard_context_contains_counts_and_recent_items(self):
        first_property = create_property(owner=self.user, title='Elso sajat hirdetes')
        second_property = create_property(owner=self.user, title='Masodik sajat hirdetes')
        other_property = create_property(title='Mas hirdetese')
        Favorite.objects.create(user=self.user, property=other_property)
        PropertyImage.objects.create(property=first_property, image=test_image_file(name='dashboard-gallery.png'))
        ContactMessage.objects.create(
            sender=self.sender,
            recipient=self.user,
            property=second_property,
            message='Dashboard teszt uzenet.',
        )

        response = self.client.get(reverse('profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user_property_count'], 2)
        self.assertEqual(response.context['favorite_count'], 1)
        self.assertEqual(response.context['received_message_count'], 1)
        self.assertEqual(response.context['gallery_image_count'], 1)
        self.assertEqual(list(response.context['recent_properties']), [second_property, first_property])
        self.assertEqual(response.context['recent_messages'][0].message, 'Dashboard teszt uzenet.')
        self.assertContains(response, 'Galériaképek')
        self.assertContains(response, 'Legutóbbi aktivitás')


class FavoriteTests(TestCase):
    def setUp(self):
        self.user = create_user('favoriteuser')
        self.property = create_property(title='Kedvenc lakas')

    def test_authenticated_user_can_add_property_to_favorites(self):
        self.client.login(username='favoriteuser', password='StrongPass123')

        response = self.client.post(reverse('toggle_favorite', args=[self.property.pk]))

        self.assertRedirects(response, reverse('property_detail', args=[self.property.pk]))
        self.assertTrue(Favorite.objects.filter(user=self.user, property=self.property).exists())

    def test_authenticated_user_can_remove_property_from_favorites(self):
        Favorite.objects.create(user=self.user, property=self.property)
        self.client.login(username='favoriteuser', password='StrongPass123')

        response = self.client.post(reverse('toggle_favorite', args=[self.property.pk]))

        self.assertRedirects(response, reverse('property_detail', args=[self.property.pk]))
        self.assertFalse(Favorite.objects.filter(user=self.user, property=self.property).exists())

    def test_anonymous_user_is_redirected_to_login_when_toggling_favorite(self):
        response = self.client.post(reverse('toggle_favorite', args=[self.property.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
        self.assertFalse(Favorite.objects.exists())

    def test_favorites_page_lists_users_favorites(self):
        other_property = create_property(title='Masik lakas')
        Favorite.objects.create(user=self.user, property=self.property)
        self.client.login(username='favoriteuser', password='StrongPass123')

        response = self.client.get(reverse('favorites'))

        self.assertEqual(response.status_code, 200)
        properties = list(response.context['properties'])
        self.assertEqual(properties, [self.property])
        self.assertContains(response, 'Kedvenc lakas')
        self.assertNotContains(response, other_property.title)

    def test_list_page_marks_favorite_property(self):
        Favorite.objects.create(user=self.user, property=self.property)
        self.client.login(username='favoriteuser', password='StrongPass123')

        response = self.client.get(reverse('listings'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.property.pk, response.context['favorite_property_ids'])
        self.assertContains(response, 'Kedvenc eltávolítása')

    def test_detail_page_marks_favorite_property(self):
        Favorite.objects.create(user=self.user, property=self.property)
        self.client.login(username='favoriteuser', password='StrongPass123')

        response = self.client.get(reverse('property_detail', args=[self.property.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_favorite'])
        self.assertContains(response, 'Kedvenc eltávolítása')


class ContactMessageTests(TestCase):
    def setUp(self):
        self.owner = create_user('messageowner')
        self.sender = create_user('messagesender')
        self.property = create_property(owner=self.owner, title='Uzenetes lakas')

    def test_authenticated_user_can_send_message_to_property_owner(self):
        self.client.login(username='messagesender', password='StrongPass123')

        response = self.client.post(
            reverse('property_detail', args=[self.property.pk]),
            {'message': 'Erdekel az ingatlan, mikor lehet megnezni?'},
        )

        self.assertRedirects(response, reverse('property_detail', args=[self.property.pk]))
        contact_message = ContactMessage.objects.get()
        self.assertEqual(contact_message.sender, self.sender)
        self.assertEqual(contact_message.recipient, self.owner)
        self.assertEqual(contact_message.property, self.property)
        self.assertEqual(contact_message.message, 'Erdekel az ingatlan, mikor lehet megnezni?')

    def test_user_cannot_send_message_to_own_property(self):
        self.client.login(username='messageowner', password='StrongPass123')

        response = self.client.post(
            reverse('property_detail', args=[self.property.pk]),
            {'message': 'Sajat hirdetesre nem lehet irni.'},
        )

        self.assertRedirects(response, reverse('property_detail', args=[self.property.pk]))
        self.assertFalse(ContactMessage.objects.exists())

    def test_anonymous_user_is_redirected_to_login_when_sending_message(self):
        response = self.client.post(
            reverse('property_detail', args=[self.property.pk]),
            {'message': 'Vendeg uzenet.'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse('login')))
        self.assertFalse(ContactMessage.objects.exists())

    def test_inbox_lists_only_received_messages(self):
        other_user = create_user('otherrecipient')
        other_property = create_property(owner=other_user, title='Masik hirdetes')
        ContactMessage.objects.create(
            sender=self.sender,
            recipient=self.owner,
            property=self.property,
            message='Ezt latnia kell a tulajdonosnak.',
        )
        ContactMessage.objects.create(
            sender=self.sender,
            recipient=other_user,
            property=other_property,
            message='Ezt nem latja a tulajdonos.',
        )
        self.client.login(username='messageowner', password='StrongPass123')

        response = self.client.get(reverse('inbox'))

        self.assertEqual(response.status_code, 200)
        received_messages = list(response.context['received_messages'])
        self.assertEqual(len(received_messages), 1)
        self.assertEqual(received_messages[0].recipient, self.owner)
        self.assertContains(response, 'Ezt latnia kell a tulajdonosnak.')
        self.assertNotContains(response, 'Ezt nem latja a tulajdonos.')

    def test_detail_page_shows_contact_form_to_non_owner(self):
        self.client.login(username='messagesender', password='StrongPass123')

        response = self.client.get(reverse('property_detail', args=[self.property.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['can_contact'])
        self.assertContains(response, 'Üzenet küldése')

    def test_detail_page_hides_contact_form_from_owner(self):
        self.client.login(username='messageowner', password='StrongPass123')

        response = self.client.get(reverse('property_detail', args=[self.property.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['can_contact'])
        self.assertContains(response, 'magadnak nem küldhetsz üzenetet')
