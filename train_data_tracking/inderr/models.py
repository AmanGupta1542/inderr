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
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, default=None)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, default=None)


class Trains(models.Model):
    name = models.CharField(max_length=255)
    number = models.IntegerField()
    from_station = models.ForeignKey('Stations', on_delete=models.CASCADE, related_name='from_station_f')
    to_station = models.ForeignKey('Stations', on_delete=models.CASCADE, related_name='to_station_f')
    inserted_at = models.DateTimeField(auto_now_add=True)
    sunday = models.BooleanField(null=True, default=None)
    monday = models.BooleanField(null=True, default=None)
    tuesday = models.BooleanField(null=True, default=None)
    wednesday = models.BooleanField(null=True, default=None)
    thursday = models.BooleanField(null=True, default=None)
    friday = models.BooleanField(null=True, default=None)
    saturday = models.BooleanField(null=True, default=None)

class TrainInnerStation(models.Model):
    train_id = models.ForeignKey('Trains', on_delete=models.CASCADE)
    # prev_station_id = models.ForeignKey('Stations', on_delete=models.CASCADE, related_name='prev_station')
    station_id = models.ForeignKey('Stations', on_delete=models.CASCADE)
    # next_station_id = models.ForeignKey('Stations', on_delete=models.CASCADE, related_name='next_station')
    order = models.IntegerField()
    inserted_at = models.DateTimeField(auto_now_add=True)
    arrives = models.TimeField(null=True, default=None)
    departs = models.TimeField(null=True, default=None)
    halt_time = models.IntegerField(null=True, default=None)
    distance = models.FloatField(null=True, default=None)
    avg_delay = models.IntegerField(null=True, default=None)
    day = models.IntegerField(null=True, default=None)
    is_stop = models.BooleanField( default=False)

class Temp(models.Model):
    name = models.CharField(max_length=1000)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, default=None)
    lon = models.DecimalField(max_digits=9, decimal_places=6, null=True, default=None)
    inserted_at = models.DateTimeField(auto_now_add=True)


class UploadImage(models.Model):  
    caption = models.CharField(max_length=200)  
    image = models.ImageField(upload_to='images')  
  
    def __str__(self):  
        return self.caption  
    
class ConfigInfo(models.Model):
    train = models.ForeignKey('Trains', on_delete=models.CASCADE)
    coach_no = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.train.name} - Coach No: {self.coach_no}"