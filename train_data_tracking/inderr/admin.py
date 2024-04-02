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
    list_display = ('id', 'name', 'code', 'district_id', 'divisions_id', 'lat', 'lon')

admin.site.register(Stations, StationsAdmin)

class TrainsAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'number', 'from_station','to_station', 'inserted_at')

admin.site.register(Trains, TrainsAdmin)

class TrainInnerStationAdmin (admin.ModelAdmin):
    list_display = ('id', 'train_id', 'station_id', 'order', 'inserted_at')

admin.site.register(TrainInnerStation, TrainInnerStationAdmin)

@admin.register(ConfigInfo)
class ConfigInfoAdmin(admin.ModelAdmin):
    list_display = ['id', 'train', 'coach_no']