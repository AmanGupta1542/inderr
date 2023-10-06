from django.contrib import admin
from .models import *

# Register your models here.
class CountriesAdmin (admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'phone','symbol', 'capital', 'currency', 'continent', 'continentCode', 'alpha3')

admin.site.register(Countries, CountriesAdmin)

class StatesAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'country_id', 'inserted_at')

admin.site.register(States, StatesAdmin)

class DivisionsAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'state_id', 'inserted_at')

admin.site.register(Divisions, DivisionsAdmin)

class DistrictAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'division_id', 'inserted_at')

admin.site.register(District, DistrictAdmin)

class StationsAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'district_id', 'divisions_id')

admin.site.register(Stations, StationsAdmin)

class TrainsAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'number', 'from_station','to_station', 'inserted_at')

admin.site.register(Trains, TrainsAdmin)