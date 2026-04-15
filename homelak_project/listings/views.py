from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PropertyForm
from .models import Property


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

    context = {
        'properties': properties,
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
    context = {
        'property': property_obj,
        'related_properties': related_properties,
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
    user_properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    context = {
        'user_properties': user_properties,
        'user_property_count': user_properties.count(),
    }
    return render(request, 'fiok.html', context)


@login_required
def create_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()
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
            return redirect('property_detail', pk=updated_property.pk)
    else:
        form = PropertyForm(instance=property_obj)

    return render(
        request,
        'ingatlan_feltoltes.html',
        {
            'form': form,
            'property': property_obj,
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
