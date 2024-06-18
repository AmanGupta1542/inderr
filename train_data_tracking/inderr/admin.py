from django.contrib import admin
from .models import *

# Register your models here.
class CountriesAdmin (admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'phone','symbol', 'capital', 'currency', 'continent', 'continentCode', 'alpha3')

admin.site.register(Countries, CountriesAdmin)

class StatesAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'country_id', 'official_language', 'language_code', 'has_translator', 'inserted_at')

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


class TrackingDataAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'lat', 'lon', 'curr_lat', 'curr_lon', 'order',
        'remaining_distance', 'is_crossed', 'actual_arrival_time',
        'actual_departure_time', 'abbr', 'distance', 'total_distance',
        'estimate_time', 'depart_time', 'halt_time', 'total_time_to_reach',
        'instant_distance', 'instant_speed', 'late_by', 'user', 'config', 'timestamp'
    )
    search_fields = ('name', 'abbr')
    list_filter = ('is_crossed', 'estimate_time', 'depart_time')
    ordering = ('order',)

admin.site.register(TrackingData, TrackingDataAdmin)

@admin.register(LoginInfo)
class LoginInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time')