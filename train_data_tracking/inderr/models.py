from django.db import models
from django.contrib.auth.models import User

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
    official_language = models.CharField(max_length=100)
    language_code = models.CharField(max_length=10)
    has_translator = models.BooleanField(default=True)

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
    user_id = models.ForeignKey(User, on_delete=models.RESTRICT)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.train.name} - Coach No: {self.coach_no}"
    

class TrackingData(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    curr_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    curr_lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    remaining_distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    is_crossed = models.BooleanField(default=False)
    actual_arrival_time = models.DateTimeField(blank=True, null=True)
    actual_departure_time = models.DateTimeField(blank=True, null=True)
    abbr = models.CharField(max_length=10, blank=True, null=True)
    distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    total_distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    estimate_time = models.TimeField(blank=True, null=True)
    depart_time = models.TimeField(blank=True, null=True)
    halt_time = models.IntegerField(blank=True, null=True)
    total_time_to_reach = models.DateTimeField(blank=True, null=True)
    instant_distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    instant_speed = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    late_by = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    config = models.ForeignKey(ConfigInfo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or f"Station {self.id}"
    

class TrackingDataHistory(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    curr_lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    curr_lon = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)
    remaining_distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    is_crossed = models.BooleanField(default=False)
    actual_arrival_time = models.DateTimeField(blank=True, null=True)
    actual_departure_time = models.DateTimeField(blank=True, null=True)
    abbr = models.CharField(max_length=10, blank=True, null=True)
    distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    total_distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    estimate_time = models.TimeField(blank=True, null=True)
    depart_time = models.TimeField(blank=True, null=True)
    halt_time = models.IntegerField(blank=True, null=True)
    total_time_to_reach = models.DateTimeField(blank=True, null=True)
    instant_distance = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    instant_speed = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    late_by = models.CharField(max_length=255, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    config = models.ForeignKey(ConfigInfo, on_delete=models.CASCADE)

    def __str__(self):
        return self.name or f"Station {self.id}"
    

class LoginInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    

class RestartLogs(models.Model):
    config_id = models.BigIntegerField()
    tracking_log_id = models.BigIntegerField()