from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import pickle
import sys
from django.db.models import Q
from datetime import datetime, time

from .forms import UserLogin, UserImage
from .models import Trains, TrainInnerStation, UploadImage, Temp
from .coords import get_coords, next_coords
from .public_functions import *

# Create your views here.

def index(request):
    if request.user.is_authenticated:
        return render(request, 'inderr/dashboard.html')
    else:
        return redirect('/login')


def change_password(request):
    if request.user.is_authenticated:
        return render(request, 'inderr/change-password.html')
    else:
        return redirect('/login')

def user_login(request):
    # if request.user.is_authenticated:
    #     return redirect("/")
    if request.user.is_authenticated:
        return redirect('/')
    else :
        if request.method == "POST":
            form = UserLogin(request.POST)
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, f"You are now logged in as {username}.")
                    return redirect("/")
                else:
                    messages.error(request,"Invalid username or password.")
            else:
                messages.error(request,"Invalid username or password.")
        form = UserLogin()
        return render(request=request, template_name="inderr/login.html", context={"login_form":form, "no_base_load":True})


def user_logout(request):
	logout(request)
	messages.info(request, "You have successfully logged out.") 
	return redirect("/login")


def trains(request):
    if request.user.is_authenticated:
        object_list = Trains.objects.all()
        items_per_page = 10
        paginator = Paginator(object_list, items_per_page)
        # print(paginator)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        return render(request, 'inderr/trains.html', context)
    else :
        return redirect('/')

def emit_rpi_data(request, data):
    import socket
    # Define the Raspberry Pi's IP address and port
    raspberry_pi_ip = '192.168.43.15'  # aman wifi
    #raspberry_pi_ip = '192.168.137.8'
    # raspberry_pi_ip = '192.168.31.89'  # madhya airtel
    raspberry_pi_port = 1026
    try:
        print('try connecting')
        print('final data')
        print(data)
        # print(request.session.get('train_stations'))
        train_stations = request.session.get('train_stations')
        train_stations['next_station'] = data['next_station']
        train_stations['curr_location'] = data['curr_location']
        train_stations['speed'] = data['speed']
        train_stations['late_by'] = data['late_by']
        print(train_stations)
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the Raspberry Pi
        client_socket.connect((raspberry_pi_ip, raspberry_pi_port))

        # Send data to the Raspberry Pi
        # data = "Hello, Raspberry Pi!"
        # data = data['next_stations']
        print('final data')
        
        # train_stations = request.session.get('train_stations')
        # data = train_stations.update(data)
        # print(data)
        print("Size of data_list:", sys.getsizeof(train_stations), "bytes")
        # Serialize the dictionary object using pickle
        serialized_data = pickle.dumps(train_stations)
        # serialized_data = json.dumps(data).encode('utf-8')
        client_socket.send(serialized_data)
        # Close the socket
        client_socket.close()
        return JsonResponse({'success': 'Called Successfully'}, status=200)
    except socket.gaierror as e:
        print({'error': f"An error occurred: {e}"})
        return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
        # return f"Socket error: {e}"
    except Exception as e:
        print({'error': f"An error occurred: {e}"})
        return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
        # return f"An error occurred: {e}"

def train_details(request, train_number):
    if request.user.is_authenticated:
        train = Trains.objects.get(number=train_number)
        object_list = TrainInnerStation.objects.filter(train_id=train).order_by('order')
        places = Temp.objects.all()

        print(train.id)
        next_stations = get_next_station(train.id)
        # stop_stations = TrainInnerStation.objects.filter(train_id=train.id).order_by('order')
        # curr_location = get_coords()
        # if curr_location['lat'] != 0 and curr_location['lon'] != 0 :
        #     stop_list = []
        #     for stations in stop_stations:
        #         # print(stations.station_id.name)
        #         dict = {
        #                 'name': stations.station_id.name,
        #                 'lat': stations.station_id.lat,
        #                 'lon':stations.station_id.lon,
        #                 'order': stations.order,
        #                 'distance': haversine_distance(curr_location['lat'], curr_location['lon'], stations.station_id.lat, stations.station_id.lon)
        #             }
        #         stop_list.append(dict)
        #     from_station = stop_list[0]
        #     sorted_stations = stop_list
        #     sorted_stations.sort(key=lambda x: x['distance'])
        #     min_stat = sorted_stations[0]

        #     # From station to current location (selected place)
        #     FSTCL = haversine_distance(from_station['lat'], from_station['lon'], curr_location['lat'], curr_location['lon'])

        #     # From station to miminum station (min_stat)
        #     FSTMS = haversine_distance(from_station['lat'], from_station['lon'], min_stat['lat'], min_stat['lon'])
        #     if(FSTMS < FSTCL or FSTMS == 0):
        #         next_stations = [stat for stat in sorted_stations if min_stat['order']+1 == stat['order']][0]
        #     else :
        #         next_stations = min_stat
        current_time = datetime.now().time()
        # Convert the current time to a datetime object with today's date
        current_datetime = datetime.combine(datetime.today(), current_time)
        late_by_min = (current_datetime - datetime.combine(datetime.today(), object_list[0].departs)).total_seconds() / 60
        late_by = 0 if late_by_min < 0 else round(late_by_min, 0)
        context = {'train': train, 'object_list':object_list, 'places':places, 'curr_location':get_coords(), 'next_stations':next_stations }
        print("emit_rpi_data call")
        stations = []
        total_distance = 0
        for station in object_list:
            if station.distance: total_distance +=station.distance
            stations.append({
                'name': station.station_id.name,
                'abbr': station.station_id.code,
                'distance': station.distance,
                'total_distance': total_distance,
                'order': station.order,
                'estimate_time': station.arrives.strftime('%H:%M') if station.arrives is not None else None,
                'delay_time': station.departs.strftime('%H:%M') if station.departs is not None else None,
                'lat': str(station.station_id.lat),
                'lon': str(station.station_id.lon),
                'halt_time': station.halt_time
            })
        res_data = {
            'train': {
                'name': train.name,
                'number': train.number,
                'from_station': train.from_station.name,
                'to_station': train.to_station.name
            },
            'stations': stations,
            # 'next_station':next_stations,
            # 'curr_location':get_coords(),
            # 'speed': 0,
            # 'late_by': late_by
        }
        # print(res_data)
        # serialized_data = pickle.dumps(res_data)
        # print('data serialized')
        # print(serialized_data)
        # deserialized_data = pickle.loads(serialized_data, encoding='utf-8')
        # print('deserialized data')
        # print(deserialized_data)
        # emit_rpi_data(request, res_data)
        request.session['train_stations'] = res_data
        return render(request, 'inderr/train-details.html', context)
        context = {
            # 'train': {
            #     'id': 3,
            #     'name': 'rj',
            #     'number': 12161,
            #     'inserted_at': '',
            #     'from_station': {
            #         'name': 'Bhopal', 
            #         'lat': Decimal('24.172716'), 
            #         'lon': Decimal('78.184876'), 
            #         'code': 'BPL', 
            #         'distance': 10.97408434219449
            #     },
            #     'to_station': {
            #         'name': 'Damoh', 
            #         'lat': Decimal('24.172716'), 
            #         'lon': Decimal('78.184876'), 
            #         'code': "DMO", 
            #     },
            #     'monday': true,
            #     'tuesday': false,
            # },
            # 'object_list': [
            #     {
            #         'id': 8,
            #         'order': 1,
            #         'inserted_at': '',
            #         'station_id': {
            #             'name': 'Bhopal', 
            #             'lat': Decimal('24.172716'), 
            #             'lon': Decimal('78.184876'), 
            #             'code': 'BPL',
            #         },
            #         'train_id': {
            #             'id': 3,
            #             'name': 'rj',
            #             'number': 12161,
            #             'inserted_at': '',
            #             'from_station': {
            #                 'name': 'Bhopal', 
            #                 'lat': Decimal('24.172716'), 
            #                 'lon': Decimal('78.184876'), 
            #                 'order': 1, 
            #                 'distance': 10.97408434219449
            #             },
            #             'to_station': {
            #                 'name': 'Damoh', 
            #                 'lat': Decimal('24.172716'), 
            #                 'lon': Decimal('78.184876'), 
            #                 'order': 12, 
            #                 'distance': 10.97408434219449
            #             },
            #             'monday': true,
            #             'tuesday': false,
            #         },
            #         'arrives': 44,
            #         'avg_delay': 2,
            #         'day': 1,
            #         'departs': 12.40,
            #         'distance': '30km',
            #         'halt_time': "2 min",
            #         "is_stop": True
            #     },
            #     {
            #         'id': 7,
            #         'order': 2,
            #         'inserted_at': '',
            #         'station_id': {
            #             'name': 'Vidisha', 
            #             'lat': Decimal('24.172716'), 
            #             'lon': Decimal('78.184876'),
            #             'code': 'VHS'
            #         },
            #         'train_id': {
            #             'id': 3,
            #             'name': 'rj',
            #             'number': 12161,
            #             'inserted_at': '',
            #             'from_station': {
            #                 'name': 'Bhopal', 
            #                 'lat': Decimal('24.172716'), 
            #                 'lon': Decimal('78.184876'), 
            #                 'order': 1, 
            #                 'distance': 10.97408434219449
            #             },
            #             'to_station': {
            #                 'name': 'Damoh', 
            #                 'lat': Decimal('24.172716'), 
            #                 'lon': Decimal('78.184876'), 
            #                 'order': 12, 
            #                 'distance': 10.97408434219449
            #             },
            #             'monday': true,
            #             'tuesday': false,
            #         },
            #         'arrives': 44,
            #         'avg_delay': 2,
            #         'day': 1,
            #         'departs': 12.40,
            #         'distance': '30km',
            #         'halt_time': "2 min",
            #         "is_stop": True
            #     },
                
            # ],
            # 'curr_location': {
            #     'lat': Decimal('24.115625'), 
            #     'lon': Decimal('78.111797')
            # },
            # 'next_stations': {
            #     'name': 'Bina', 
            #     'lat': Decimal('24.172716'), 
            #     'lon': Decimal('78.184876'), 
            #     'order': 5, 
            #     'distance': 10.97408434219449
            # },
            # 'speed': 0,
            # 'late_by': 3
        }
        
    else :
        return redirect('/')

def file_uploads(request):
    if request.user.is_authenticated:
        if request.method == 'POST':  
            form = UserImage(request.POST, request.FILES)  
            if form.is_valid():  
                form.save()  
    
                # Getting the current instance object to display in the template  
                img_object = form.instance  
                
                return render(request, 'inderr/file_uploads.html', {'form': form, 'img_obj': img_object})  
        else:  
            form = UserImage()  
     
        return render(request, 'inderr/file_uploads.html', {'form' : form})
    else :
        return redirect('/')


def cal_distance(request):
    if request.user.is_authenticated:
        places = Temp.objects.all()
        context = {'places':places}
        return render(request, 'inderr/map-distance.html', context)
    else :
        return redirect('/')

def get_lat_lon(request): # May include more arguments depending on URL parameters
    # Get data from the database - Ex. Model.object.get(...)
    place_name = json.load(request)['place_name']
    # print(place_name)
    place = Temp.objects.get(name=place_name)
    other_places = Temp.objects.filter(~Q(name=place_name))
    places_list = []
    for pla in other_places:
        dict = {
                'name': pla.name,
                'lat': pla.lat,
                'lon':pla.lon
            }
        places_list.append(dict)

    data = {
            'place':{
                'name': place.name,
                'lat': place.lat,
                'lon':place.lon
            },
            'other_places': places_list
    }
    # print(data)
    return JsonResponse(data,safe=False)

def get_lat_lon2(request): # May include more arguments depending on URL parameters
    # Get data from the database - Ex. Model.object.get(...)
    if request.method == 'POST':
        details = json.load(request)['details']
        place = Temp.objects.get(name=details['place_name'])
        stop_stations = TrainInnerStation.objects.filter(train_id=details['train_id']).order_by('order')
        print(details)
        # print(place)
        # print(object_list)

        stop_list = []
        for stations in stop_stations:
            # print(stations.station_id.name)
            dict = {
                    'name': stations.station_id.name,
                    'lat': stations.station_id.lat,
                    'lon':stations.station_id.lon,
                    'order': stations.order
                }
            stop_list.append(dict)

        data = {
                'place':{
                    'name': place.name,
                    'lat': place.lat,
                    'lon':place.lon
                },
                'stop_list': stop_list,
                'from_station': stop_list[0]
        }
        # print(data)
        return JsonResponse(data,safe=False)

    return JsonResponse({'error': 'Method not allowed'}, status=403)

def send_data_rsp(request):
    if request.method == 'POST':
        import socket
        data = json.load(request)['data']
        print(data)
        # 'next_station':next_stations,
        # 'curr_location':get_coords(),
        # 'speed': 0,
        # 'late_by': late_by
        data['curr_location'] = get_coords()
        data['speed'] = 0
        data['late_by'] = 0
        print(data)
        emit_rpi_data(request, data)
        # # Define the Raspberry Pi's IP address and port
        # # raspberry_pi_ip = '192.168.43.15'  # aman wifi
        # #raspberry_pi_ip = '192.168.137.8'
        # raspberry_pi_ip = '192.168.31.89'  # madhya airtel
        # raspberry_pi_port = 1026
        # try:
        #     # Create a socket object
        #     client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #     # Connect to the Raspberry Pi
        #     client_socket.connect((raspberry_pi_ip, raspberry_pi_port))

        #     # Send data to the Raspberry Pi
        #     # data = "Hello, Raspberry Pi!"
        #     data = data['next_stations']
        #     print(data)
        #     client_socket.send(data.encode('utf-8'))
        #     # Close the socket
        #     client_socket.close()
        #     return JsonResponse({'success': 'Called Successfully'}, status=200)
        # except socket.gaierror as e:
        #     return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
        #     # return f"Socket error: {e}"
        # except Exception as e:
        #     return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
        #     # return f"An error occurred: {e}"
    return JsonResponse({'error': 'Method not allowed'}, status=403)

def get_updated_info(request):
    if request.method == 'POST':
        details = json.load(request)['details']
        train_id = details['train_id']
        data = get_next_station(train_id)
        return JsonResponse({'success': 'Called Successfully', 'data': data}, status=200)
    return JsonResponse({'error': 'Method not allowed'}, status=403)
