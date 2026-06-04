from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import ContactMessageForm, PropertyForm
from .models import ContactMessage, Favorite, Property, PropertyImage


def home(request):
    latest_properties = Property.objects.order_by('-created_at')[:3]
    return render(request, 'index.html', {'latest_properties': latest_properties})


def listings(request):
    properties = Property.objects.select_related('owner').all()

    location = request.GET.get('location', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    min_rooms = request.GET.get('min_rooms', '').strip()
    sort = request.GET.get('sort', 'newest').strip()

    if location:
        properties = properties.filter(location__icontains=location)

    if min_price.isdigit():
        properties = properties.filter(price__gte=int(min_price))

    if max_price.isdigit():
        properties = properties.filter(price__lte=int(max_price))

    if min_rooms.isdigit():
        properties = properties.filter(rooms__gte=int(min_rooms))

    sort_options = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price',
        'rooms_desc': '-rooms',
        'sqm_desc': '-sq_meter',
    }
    properties = properties.order_by(sort_options.get(sort, '-created_at'))
    paginator = Paginator(properties, 6)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)
    favorite_property_ids = set()

    if request.user.is_authenticated:
        favorite_property_ids = set(
            Favorite.objects.filter(user=request.user, property__in=page_obj.object_list)
            .values_list('property_id', flat=True)
        )

    context = {
        'properties': page_obj.object_list,
        'page_obj': page_obj,
        'paginator': paginator,
        'page_querystring': query_params.urlencode(),
        'favorite_property_ids': favorite_property_ids,
        'filters': {
            'location': location,
            'min_price': min_price,
            'max_price': max_price,
            'min_rooms': min_rooms,
            'sort': sort if sort in sort_options else 'newest',
        },
        'result_count': properties.count(),
    }
    return render(request, 'ingatlanok.html', context)


def property_detail(request, pk):
    property_obj = get_object_or_404(Property.objects.select_related('owner'), pk=pk)
    related_properties = Property.objects.exclude(pk=property_obj.pk).order_by('-created_at')[:3]
    gallery_images = property_obj.gallery_images.all()
    is_favorite = False
    can_contact = (
        request.user.is_authenticated
        and property_obj.owner is not None
        and property_obj.owner != request.user
    )
    contact_form = ContactMessageForm()

    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, property=property_obj).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'{reverse("login")}?next={request.path}')

        if not can_contact:
            messages.error(request, 'Erre a hirdetésre nem küldhetsz üzenetet.')
            return redirect('property_detail', pk=property_obj.pk)

        contact_form = ContactMessageForm(request.POST)
        if contact_form.is_valid():
            contact_message = contact_form.save(commit=False)
            contact_message.sender = request.user
            contact_message.recipient = property_obj.owner
            contact_message.property = property_obj
            contact_message.save()
            messages.success(request, 'Az üzenetedet elküldtük a hirdetés feltöltőjének.')
            return redirect('property_detail', pk=property_obj.pk)

    context = {
        'property': property_obj,
        'related_properties': related_properties,
        'gallery_images': gallery_images,
        'is_favorite': is_favorite,
        'can_contact': can_contact,
        'contact_form': contact_form,
    }
    return render(request, 'ingatlan_reszletek.html', context)


def login_view(request):
    return render(request, 'belepes.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    user_properties = Property.objects.filter(owner=request.user).order_by('-created_at', '-pk')
    favorite_count = Favorite.objects.filter(user=request.user).count()
    received_messages = (
        ContactMessage.objects.filter(recipient=request.user)
        .select_related('sender', 'property')
        .order_by('-created_at')
    )
    received_message_count = received_messages.count()
    user_property_count = user_properties.count()
    gallery_image_count = PropertyImage.objects.filter(property__owner=request.user).count()
    context = {
        'user_properties': user_properties,
        'user_property_count': user_property_count,
        'favorite_count': favorite_count,
        'received_message_count': received_message_count,
        'gallery_image_count': gallery_image_count,
        'recent_properties': user_properties[:3],
        'recent_messages': received_messages[:3],
    }
    return render(request, 'fiok.html', context)


@login_required
def inbox(request):
    received_messages = (
        ContactMessage.objects.filter(recipient=request.user)
        .select_related('sender', 'property')
        .order_by('-created_at')
    )
    return render(
        request,
        'uzenetek.html',
        {
            'received_messages': received_messages,
            'received_message_count': received_messages.count(),
        },
    )


@login_required
def favorites(request):
    favorite_properties = (
        Property.objects.filter(favorited_by__user=request.user)
        .select_related('owner')
        .order_by('-favorited_by__created_at')
    )
    favorite_property_ids = set(favorite_properties.values_list('pk', flat=True))
    context = {
        'properties': favorite_properties,
        'favorite_property_ids': favorite_property_ids,
        'favorite_count': favorite_properties.count(),
    }
    return render(request, 'kedvencek.html', context)


@login_required
def toggle_favorite(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)

    if request.method == 'POST':
        favorite, created = Favorite.objects.get_or_create(user=request.user, property=property_obj)
        if not created:
            favorite.delete()

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or reverse('property_detail', args=[pk])
    return redirect(next_url)


@login_required
def create_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
            save_gallery_images(property_obj, form.cleaned_data.get('gallery_images', []))
            return redirect('property_detail', pk=property_obj.pk)
    else:
        form = PropertyForm()

    return render(
        request,
        'ingatlan_feltoltes.html',
        {
            'form': form,
            'page_title': 'Új ingatlan feltöltése',
            'form_title': 'Hirdetés feladása',
            'submit_label': 'Hirdetés mentése',
            'is_edit': False,
        },
    )


@login_required
def edit_property(request, pk):
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            updated_property = form.save(commit=False)
            updated_property.owner = request.user
            updated_property.save()
            delete_gallery_images(property_obj, request.POST.getlist('delete_gallery_images'))
            save_gallery_images(updated_property, form.cleaned_data.get('gallery_images', []))
            return redirect('property_detail', pk=updated_property.pk)
    else:
        form = PropertyForm(instance=property_obj)

    return render(
        request,
        'ingatlan_feltoltes.html',
        {
            'form': form,
            'property': property_obj,
            'gallery_images': property_obj.gallery_images.all(),
            'page_title': f'Szerkesztés - {property_obj.title}',
            'form_title': 'Hirdetés szerkesztése',
            'submit_label': 'Módosítások mentése',
            'is_edit': True,
        },
    )


@login_required
def delete_property(request, pk):
    property_obj = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == 'POST':
        property_obj.delete()
        return redirect('profile')

    return render(request, 'ingatlan_torles.html', {'property': property_obj})


def save_gallery_images(property_obj, gallery_images):
    for image in gallery_images:
        PropertyImage.objects.create(property=property_obj, image=image)


def delete_gallery_images(property_obj, image_ids):
    if not image_ids:
        return

    property_obj.gallery_images.filter(pk__in=image_ids).delete()
