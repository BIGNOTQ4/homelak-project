from django import forms
from PIL import Image

from .models import ContactMessage, Property


MAX_IMAGE_UPLOAD_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp', 'image/gif'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput(attrs={'accept': 'image/*', 'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        if not data:
            return []

        files = data if isinstance(data, (list, tuple)) else [data]
        return [super(MultipleFileField, self).clean(file, initial) for file in files]


def validate_uploaded_image(image):
    if image.size > MAX_IMAGE_UPLOAD_SIZE:
        raise forms.ValidationError('A feltöltött kép legfeljebb 5 MB méretű lehet.')

    extension = f'.{image.name.rsplit(".", 1)[-1].lower()}' if '.' in image.name else ''
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise forms.ValidationError('Csak JPG, PNG, WEBP vagy GIF képfájl tölthető fel.')

    content_type = getattr(image, 'content_type', '')
    if content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise forms.ValidationError('Csak JPG, PNG, WEBP vagy GIF képfájl tölthető fel.')

    try:
        image.seek(0)
        Image.open(image).verify()
    except Exception as exc:
        raise forms.ValidationError('A feltöltött fájl nem érvényes képfájl.') from exc
    finally:
        image.seek(0)


class PropertyForm(forms.ModelForm):
    gallery_images = MultipleFileField(
        required=False,
        label='Galériaképek',
        help_text='Egyszerre több JPG, PNG, WEBP vagy GIF kép is feltölthető, képenként legfeljebb 5 MB méretben.',
    )

    class Meta:
        model = Property
        fields = ['title', 'location', 'price', 'sq_meter', 'rooms', 'description', 'image_url', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Pl. Modern lakás a belvárosban'}),
            'location': forms.TextInput(attrs={'placeholder': 'Pl. Budapest'}),
            'price': forms.NumberInput(attrs={'min': '1', 'step': '1', 'placeholder': 'Pl. 59900000'}),
            'sq_meter': forms.NumberInput(attrs={'min': '1', 'step': '1', 'placeholder': 'Pl. 68'}),
            'rooms': forms.NumberInput(attrs={'min': '1', 'step': '1', 'placeholder': 'Pl. 3'}),
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Írd le röviden az ingatlant...'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'title': 'Ingatlan címe',
            'location': 'Település',
            'price': 'Ár (Ft)',
            'sq_meter': 'Alapterület (m²)',
            'rooms': 'Szobák száma',
            'description': 'Leírás',
            'image_url': 'Kép URL',
            'image': 'Kép feltöltése',
        }

    def clean_price(self):
        value = self.cleaned_data.get('price')
        if value is not None and value < 1:
            raise forms.ValidationError('Az ár csak 1 vagy annál nagyobb lehet.')
        return value

    def clean_sq_meter(self):
        value = self.cleaned_data.get('sq_meter')
        if value is not None and value < 1:
            raise forms.ValidationError('Az alapterület csak 1 vagy annál nagyobb lehet.')
        return value

    def clean_rooms(self):
        value = self.cleaned_data.get('rooms')
        if value is not None and value < 1:
            raise forms.ValidationError('A szobák száma csak 1 vagy annál nagyobb lehet.')
        return value

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        validate_uploaded_image(image)
        return image

    def clean_gallery_images(self):
        images = self.cleaned_data.get('gallery_images') or []
        for image in images:
            validate_uploaded_image(image)
        return images

    def clean(self):
        cleaned_data = super().clean()
        image_url = cleaned_data.get('image_url')
        image = cleaned_data.get('image')

        if image and image_url:
            self.add_error('image_url', 'Adj meg kép URL-t vagy tölts fel képet, de egyszerre ne mindkettőt.')

        return cleaned_data


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Írd meg röviden, miben szeretnél egyeztetni az ingatlanról...',
                }
            ),
        }
        labels = {
            'message': 'Üzenet',
        }
