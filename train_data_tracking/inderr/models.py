from django.db import models

# Create your models here.
class Countries(models.Model):
    code = models.CharField(max_length=2)
    name = models.CharField(max_length=255, unique=True)
    phone = models.CharField(max_length=15)
    symbol = models.CharField(max_length=10)
    capital = models.CharField(max_length=255)
    currency = models.CharField(max_length=3)
    continent = models.CharField(max_length=100)
    continentCode = models.CharField(max_length=2)
    alpha3 = models.CharField(max_length=3)

class States(models.Model):
    name = models.CharField(max_length=255)
    country_id = models.ForeignKey('Countries', on_delete=models.CASCADE)
    inserted_at = models.DateTimeField(auto_now_add=True)

class Divisions(models.Model):
    name = models.CharField(max_length=255)
    state_id = models.ForeignKey('States', on_delete=models.CASCADE)
    inserted_at = models.DateTimeField(auto_now_add=True)

class District(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=5)
    division_id = models.ForeignKey('Divisions', on_delete=models.CASCADE)
    inserted_at = models.DateTimeField(auto_now_add=True)

class Stations(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=5)
    district_id = models.ForeignKey('District', on_delete=models.CASCADE, null=True, default=None)
    divisions_id = models.ForeignKey('Divisions', on_delete=models.CASCADE, null=True, default=None)


class Trains(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    from_station = models.ForeignKey('Stations', on_delete=models.CASCADE, related_name='from_station_f')
    to_station = models.ForeignKey('Stations', on_delete=models.CASCADE, related_name='to_station_f')
    inserted_at = models.DateTimeField(auto_now_add=True)