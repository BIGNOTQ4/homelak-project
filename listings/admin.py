from django.contrib import admin

from .models import ContactMessage, Favorite, Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = ('image', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'price', 'rooms', 'owner', 'has_uploaded_image', 'created_at')
    search_fields = ('title', 'location', 'description')
    list_filter = ('location', 'rooms', 'created_at')
    inlines = [PropertyImageInline]

    @admin.display(boolean=True, description='Saját kép')
    def has_uploaded_image(self, obj):
        return bool(obj.image)


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ('property', 'created_at')
    search_fields = ('property__title', 'property__location')
    list_filter = ('created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'created_at')
    search_fields = ('user__username', 'property__title', 'property__location')
    list_filter = ('created_at',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'property', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'property__title', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)
