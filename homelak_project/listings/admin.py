from django.contrib import admin

from .models import Property


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'rooms', 'owner', 'has_uploaded_image', 'created_at')
    search_fields = ('title', 'location', 'description')
    list_filter = ('location', 'rooms', 'created_at')

    @admin.display(boolean=True, description='Saját kép')
    def has_uploaded_image(self, obj):
        return bool(obj.image)
