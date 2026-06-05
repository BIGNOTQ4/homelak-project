from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from listings.models import Property


DEMO_USERNAME = 'homelak_demo'

DEMO_IMAGE_BY_LOCATION = {
    'Budapest': 'budapest-premium-lakas.jpg',
    'Debrecen': 'debrecen-csaladi-otthon.jpg',
    'Győr': 'gyor-csaladi-haz.jpg',
    'Szeged': 'szeged-sorhaz.jpg',
    'Pécs': 'pecs-park-melletti-lakas.jpg',
    'Miskolc': 'debrecen-modern-lakas.jpg',
}

LEGACY_DEMO_TITLES = {
    'Modern lakás a belvárosban': 'budapest-premium-lakas.jpg',
    'Családi ház kerttel': 'debrecen-csaladi-otthon.jpg',
    'Panorámás tetőtéri lakás': 'pecs-panoramas-lakas.jpg',
    'Felújított garzon egyetem közelében': 'szeged-lakas.jpg',
    'Kertes sorházi lakás': 'gyor-csaladi-haz.jpg',
}

DEMO_PROPERTIES = [
    {
        'title': 'Elegáns, világos nagypolgári lakás a Belváros közelében',
        'location': 'Budapest',
        'price': 89900000,
        'sq_meter': 74,
        'rooms': 3,
        'description': (
            'Felújított, jó elrendezésű társasházi lakás tágas nappalival, két külön nyíló '
            'szobával és igényes burkolatokkal. Kiváló választás városi otthonnak vagy '
            'értékálló befektetésnek.'
        ),
        'image_name': 'budapest-premium-lakas.jpg',
    },
    {
        'title': 'Modern debreceni lakás nagy erkéllyel',
        'location': 'Debrecen',
        'price': 68900000,
        'sq_meter': 69,
        'rooms': 3,
        'description': (
            'Energiatakarékos, újszerű lakás amerikai konyhás nappalival, két hálószobával '
            'és napos erkéllyel. Rendezett környezetben, jó közlekedéssel.'
        ),
        'image_name': 'debrecen-modern-lakas.jpg',
    },
    {
        'title': 'Családi ház gondozott kerttel Győr csendes részén',
        'location': 'Győr',
        'price': 94900000,
        'sq_meter': 126,
        'rooms': 5,
        'description': (
            'Jó állapotú családi ház praktikus elrendezéssel, világos nappalival, három '
            'hálószobával és rendezett kerttel. Garázs és tároló is tartozik hozzá.'
        ),
        'image_name': 'gyor-csaladi-haz.jpg',
    },
    {
        'title': 'Fiatalos szegedi lakás egyetemhez közeli környéken',
        'location': 'Szeged',
        'price': 47900000,
        'sq_meter': 52,
        'rooms': 2,
        'description': (
            'Világos, jó állapotú lakás praktikus alaprajzzal. Ideális első otthonnak vagy '
            'kiadásra, külön konyhával és kényelmes hálószobával.'
        ),
        'image_name': 'szeged-lakas.jpg',
    },
    {
        'title': 'Panorámás pécsi lakás igényes belső terekkel',
        'location': 'Pécs',
        'price': 52900000,
        'sq_meter': 61,
        'rooms': 3,
        'description': (
            'Hangulatos, jó fényviszonyú lakás szép kilátással és átgondolt elrendezéssel. '
            'A belváros rövid idő alatt elérhető, a környék nyugodt és rendezett.'
        ),
        'image_name': 'pecs-panoramas-lakas.jpg',
    },
    {
        'title': 'Kertkapcsolatos budapesti ikerház prémium kivitelben',
        'location': 'Budapest',
        'price': 113900000,
        'sq_meter': 138,
        'rooms': 5,
        'description': (
            'Zöldövezeti, modern ikerház nagy terasszal, tágas nappalival és négy hálóval. '
            'Kényelmes családi otthon saját parkolóval és gondozható kerttel.'
        ),
        'image_name': 'budapest-ikerhaz.jpg',
    },
    {
        'title': 'Budapesti garzon modern belsővel, kiváló lokációban',
        'location': 'Budapest',
        'price': 46900000,
        'sq_meter': 35,
        'rooms': 1,
        'description': (
            'Kompakt, igényesen kialakított garzon alacsony fenntartással. Jó választás '
            'első lakásnak vagy befektetésnek, központi elhelyezkedéssel.'
        ),
        'image_name': 'budapest-garzon.jpg',
    },
    {
        'title': 'Tágas debreceni családi otthon zöld környezetben',
        'location': 'Debrecen',
        'price': 86500000,
        'sq_meter': 94,
        'rooms': 4,
        'description': (
            'Három hálószobás, családbarát otthon világos nappalival és jó tárolási '
            'lehetőségekkel. Iskola, boltok és tömegközlekedés rövid sétával elérhető.'
        ),
        'image_name': 'debrecen-csaladi-otthon.jpg',
    },
    {
        'title': 'Felújított szegedi sorház saját terasszal',
        'location': 'Szeged',
        'price': 83900000,
        'sq_meter': 103,
        'rooms': 4,
        'description': (
            'Azonnal költözhető sorházi otthon napos terasszal, modern konyhával és '
            'kényelmes családi terekkel. Csendes, mégis jól megközelíthető környéken.'
        ),
        'image_name': 'szeged-sorhaz.jpg',
    },
    {
        'title': 'Csendes pécsi lakás park mellett, jó közlekedéssel',
        'location': 'Pécs',
        'price': 41900000,
        'sq_meter': 49,
        'rooms': 2,
        'description': (
            'Világos, kényelmes két szobás lakás rendezett társasházban. A park, boltok és '
            'buszmegálló néhány perc alatt elérhető.'
        ),
        'image_name': 'pecs-park-melletti-lakas.jpg',
    },
]


class Command(BaseCommand):
    help = 'Realisztikus HomeLak demo ingatlanokat tölt fel helyi static fotókkal.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Törli a homelak_demo felhasználó korábbi demo hirdetéseit, majd újratölti őket.',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        demo_user, _ = User.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={'email': 'demo@homelak.local'},
        )
        if not demo_user.has_usable_password():
            demo_user.set_password('DemoPass123')
            demo_user.save(update_fields=['password'])

        if options['reset']:
            Property.objects.filter(owner=demo_user).delete()

        repaired_count = repair_legacy_demo_images()

        if Property.objects.filter(owner=demo_user).exists():
            if verbosity:
                if repaired_count:
                    self.stdout.write(f'{repaired_count} régi HomeLak minta hirdetés képe javítva.')
                self.stdout.write(
                    self.style.WARNING(
                        'Már vannak demo hirdetések. Újratöltéshez futtasd: '
                        'python manage.py seed_demo_properties --reset'
                    )
                )
            return

        for data in DEMO_PROPERTIES:
            property_data = data.copy()
            property_data['image_url'] = demo_image_url(property_data.pop('image_name'))
            Property.objects.create(owner=demo_user, image='', **property_data)

        if verbosity:
            self.stdout.write(self.style.SUCCESS(f'{len(DEMO_PROPERTIES)} realisztikus demo hirdetés feltöltve.'))
            if repaired_count:
                self.stdout.write(f'{repaired_count} régi HomeLak minta hirdetés képe javítva.')
            self.stdout.write('Demo felhasználó: homelak_demo / DemoPass123')


def repair_legacy_demo_images():
    repaired_count = 0

    for property_obj in Property.objects.filter(owner__isnull=True):
        image_name = LEGACY_DEMO_TITLES.get(property_obj.title)

        if image_name is None and (
            property_obj.uses_placeholder_image
            or not property_obj.image_url
            or property_obj.image_url.startswith('http')
            or property_obj.location in DEMO_IMAGE_BY_LOCATION
        ):
            image_name = DEMO_IMAGE_BY_LOCATION.get(property_obj.location, 'budapest-premium-lakas.jpg')

        if image_name is None:
            continue

        property_obj.image = ''
        property_obj.image_url = demo_image_url(image_name)
        property_obj.save(update_fields=['image', 'image_url'])
        repaired_count += 1

    return repaired_count


def demo_image_url(image_name):
    return f'{settings.STATIC_URL.rstrip("/")}/images/demo_properties/{image_name}'
