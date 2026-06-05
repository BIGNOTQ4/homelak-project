from django.core.management.base import BaseCommand

from listings.models import Property


class Command(BaseCommand):
    help = 'Listázza a placeholder képes és duplikált képet használó ingatlanokat.'

    def handle(self, *args, **options):
        problematic_properties = []
        image_usage = {}

        for property_obj in Property.objects.select_related('owner').prefetch_related('gallery_images').order_by('id'):
            uses_placeholder = property_obj.uses_placeholder_image
            if uses_placeholder:
                problematic_properties.append(property_obj)

            image_usage.setdefault(property_obj.display_image_url, []).append(property_obj)

            self.stdout.write(
                format_property_line(
                    property_obj=property_obj,
                    uses_placeholder=uses_placeholder,
                )
            )

        duplicate_groups = {
            image_url: properties
            for image_url, properties in image_usage.items()
            if len(properties) > 2 and not image_url.endswith('property-placeholder.svg')
        }

        if duplicate_groups:
            self.stdout.write('')
            self.stdout.write('Duplikált kép használat:')
            for image_url, properties in sorted(duplicate_groups.items(), key=lambda item: len(item[1]), reverse=True):
                listing_summary = ', '.join(f'#{property_obj.id} {property_obj.title}' for property_obj in properties)
                self.stdout.write(f'- {image_url}: {len(properties)} listing -> {listing_summary}')

        if problematic_properties:
            self.stdout.write(self.style.WARNING(f'{len(problematic_properties)} ingatlan használna placeholder képet.'))
        else:
            self.stdout.write(self.style.SUCCESS('0 ingatlan használna placeholder képet.'))

        if duplicate_groups:
            self.stdout.write(self.style.WARNING(f'{len(duplicate_groups)} kép több listingnél is használatban van.'))
            return

        self.stdout.write(self.style.SUCCESS('Nincs túl sokszor használt display kép.'))


def format_property_line(property_obj, uses_placeholder):
    owner = property_obj.owner.username if property_obj.owner else 'HomeLak'
    image = property_obj.image.name if property_obj.image else ''
    status = 'PLACEHOLDER' if uses_placeholder else 'OK'
    return (
        f'[{status}] '
        f'id={property_obj.id}; '
        f'cím={property_obj.title}; '
        f'város={property_obj.location}; '
        f'ár={property_obj.price}; '
        f'owner={owner}; '
        f'image={image}; '
        f'image_url={property_obj.image_url}; '
        f'display_image_url={property_obj.display_image_url}; '
        f'uses_placeholder={uses_placeholder}'
    )
