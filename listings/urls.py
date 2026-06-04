from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('ingatlanok/', views.listings, name='listings'),
    path('ingatlanok/feltoltes/', views.create_property, name='create_property'),
    path('ingatlanok/<int:pk>/', views.property_detail, name='property_detail'),
    path('ingatlanok/<int:pk>/szerkesztes/', views.edit_property, name='edit_property'),
    path('ingatlanok/<int:pk>/torles/', views.delete_property, name='delete_property'),
    path('ingatlanok/<int:pk>/kedvenc/', views.toggle_favorite, name='toggle_favorite'),
    path('kedvencek/', views.favorites, name='favorites'),
    path('uzenetek/', views.inbox, name='inbox'),
    path('regisztracio/', views.register, name='register'),
    path('fiok/', views.profile, name='profile'),
]
