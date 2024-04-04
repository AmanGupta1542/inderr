from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import pickle
import sys
import threading
import pickle
from django.db.models import Q
from datetime import datetime
import time


from .forms import UserLogin, UserImage, ConfigInfoForm
from .models import Trains, TrainInnerStation, UploadImage, Temp, ConfigInfo, Stations
from .coords import get_coords, next_coords
from .public_functions import *
from .board import LEDBoard
import serial
from .serial_connection import TIME_DELAY

BOARD_PICKLE_FILE = "board.pkl"
board_defualt_run_thread = None
board_defualt_run_thread_b = True
board_train_data_thread = None
board_train_data_thread_b = True
stop_event = threading.Event()
board_unpickle = None
LED_COL_OPT = [20, 25, 30, 35, 40, 45, 50]

def index(request):
    global board_defualt_run_thread
    global board_train_data_thread
    global board_defualt_run_thread_b
    global board_train_data_thread_b
    if request.user.is_authenticated:
        config_train_coach = ConfigInfo.objects.first()
        if config_train_coach:
            object_list = TrainInnerStation.objects.filter(train_id=config_train_coach.train).order_by('order')
            
            ctx = {'config': config_train_coach, 'object_list': object_list, 'led_col_opt': LED_COL_OPT}
            for thread in threading.enumerate():
                print(thread)
            if board_defualt_run_thread is not None and board_defualt_run_thread.is_alive():
                # Set the event to signal the thread to stop
                # stop_event.set()
                # # Wait for the thread to stop
                # board_defualt_run_thread.join()
                # # Reset the event for future use
                # stop_event.clear()
                board_defualt_run_thread_b = False
            # print(board_defualt_run_thread.is_alive())
            # print(board_defualt_run_thread)
            for thread in threading.enumerate():
                print(thread)
            print(config_train_coach.train)
            from_station = Stations.objects.get(pk = config_train_coach.train.from_station_id).name.upper()
            to_station = Stations.objects.get(pk = config_train_coach.train.to_station_id).name.upper()
            inner_stations = TrainInnerStation.objects.filter(train_id=config_train_coach.train).order_by('order')
            via_list = []
            for stat in inner_stations:
                if int(stat.order) == 1 or int(stat.order) == len(inner_stations):
                    pass
                else:
                    via_list.append(stat.station_id.name.upper())
            board_train_data = {
                'fix_part' : {
                    'coach_no': config_train_coach.coach_no.upper(),  # 'A-11'
                    'train_no': config_train_coach.train.number   # '12003'
                },
                'moving_part': {
                    'train_from_to': from_station+" TO "+to_station,
                    'train_name': config_train_coach.train.name.upper(),
                    'train_via': 'VIA '+ ', '.join(via_list)
                }
            }
            board = unpickle_board()
            ctx['time_delay'] = board.time_delay_col
            if board_train_data_thread is None or not board_train_data_thread.is_alive():
                board_train_data_thread = threading.Thread(target=board_run_train_data, args=(board_train_data,), name="BoardTrainDataThread")
                board_train_data_thread_b = True
                board_train_data_thread.start()
            return render(request, 'inderr/dashboard.html', context=ctx)
        else: 
            return redirect('/config_train_and_coach')
    else:
        # request.session['board'] = LEDBoard()
        with open(BOARD_PICKLE_FILE, 'wb') as f:
            pickle.dump(LEDBoard(), f)

        # check if this thread already running then stop this thread first
        if board_train_data_thread is not None and board_train_data_thread.is_alive():
            board_train_data_thread_b = False
            print('diabled board_train_data_thread_b')

        # Check if the thread is not already running
        if board_defualt_run_thread is None or not board_defualt_run_thread.is_alive():
            board_defualt_run_thread = threading.Thread(target=board_run_default, name="BoardDefaultRunThread")
            board_defualt_run_thread_b = True
            print('enabled board_defualt_run_thread')
            board_defualt_run_thread.start()
        return redirect('/login')

def board_run_default():
    board = unpickle_board_obj()
    if board:
        board.default_message_byte_list = None
        while board_defualt_run_thread_b:
            board.default()

def unpickle_board():
    global board_unpickle
    if board_unpickle is None:
        board_unpickle = load_led_board(BOARD_PICKLE_FILE)
        board = board_unpickle
    else:
        board = board_unpickle
    return board

def unpickle_board_obj():
    board = unpickle_board()
    print("board unpickle data")
    print(board)
    while board.occupy:
        time.sleep(1)
    return board

def board_run_train_data(board_data):
    board = unpickle_board_obj()
    board.set_data(board_data)
    while board_train_data_thread_b:
        board.start()

# Function to unpickle the LEDBoard object
def load_led_board(filename):
    with open(filename, 'rb') as file:
        board_obj = pickle.load(file)
    return board_obj

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
                    return redirect("/config_train_and_coach")
                else:
                    messages.error(request,"Invalid username or password.")
            else:
                messages.error(request,"Invalid username or password.")
        form = UserLogin()
        return render(request=request, template_name="inderr/login.html", context={"login_form":form, "no_base_load":True})


def user_logout(request):
    # truncating config info table on logout
    ConfigInfo.objects.all().delete()  # Truncate the table associated with ConfigInfo
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

def config_train_and_coach(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ConfigInfoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('/')  # Redirect to success page after form submission
        else:
            form = ConfigInfoForm()
        trains = Trains.objects.all()  # Get all trains for dropdown
        return render(request, 'inderr/config_info_form.html', {'form': form, 'trains': trains})
    else :
        return redirect('/')


def change_led_col_speed(request, led_col):
    if request.method == 'GET':
        # Process the data as needed
        try:
            board = unpickle_board()
            board.time_delay_col = led_col
            board.time_delay = 1/led_col
            # Return success response
            return JsonResponse({'message': 'LED color speed changed successfully'}, status=200)
        except Exception as e:
            # Return error response if there's an exception
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Return error response for unsupported methods
        return JsonResponse({'error': 'Method not allowed'}, status=405)