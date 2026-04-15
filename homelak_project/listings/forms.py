from django import forms

from .models import Property


class PropertyForm(forms.ModelForm):
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

    def clean(self):
        cleaned_data = super().clean()
        image_url = cleaned_data.get('image_url')
        image = cleaned_data.get('image')

        if image and image_url:
            self.add_error('image_url', 'Adj meg kép URL-t vagy tölts fel képet, de egyszerre ne mindkettőt.')

        return cleaned_data
