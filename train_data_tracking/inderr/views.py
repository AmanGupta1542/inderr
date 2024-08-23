from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
import pickle
import sys
import threading
import pickle
from django.db.models import Q
from datetime import datetime
import time as tm
import logging
logger = logging.getLogger("inderr.views")
from django.core.cache import cache
from .cache_setup import cache_init
from django.db import transaction


from .forms import UserLogin, UserImage, ConfigInfoForm
from .models import Trains, TrainInnerStation,Temp, ConfigInfo, Stations, TrackingData, LoginInfo, TrackingDataHistory
from .coords import get_coords
from .public_functions import *
from .board import LEDBoard

BOARD_PICKLE_FILE = "board.pkl"
board_defualt_run_thread = None
board_defualt_run_thread_b = True
board_train_data_thread = None
board_train_data_thread_b = True
stop_event = threading.Event()
board_unpickle = None
LED_COL_OPT = [20, 25, 30, 35, 40, 45, 50]


def check_already_config(request):
    if request.user.is_authenticated:
        config_train_coach = ConfigInfo.objects.filter(status=0, user_id=request.user).last()
        if config_train_coach:
            request.session['already_config'] = True
            last_tracking_log_id = TrackingData.objects.filter(user=request.user, config=config_train_coach).last() # getting None if no data is there
            request.session['last_tracking_log_id'] = last_tracking_log_id.id if last_tracking_log_id is not None else None
        else:
            request.session['already_config'] = False
            request.session['last_tracking_log_id'] = None

def index(request):
    cache_init()
    global board_defualt_run_thread
    global board_train_data_thread
    global board_defualt_run_thread_b
    global board_train_data_thread_b
    if request.user.is_authenticated:
        config_train_coach = ConfigInfo.objects.filter(status=0, user_id=request.user).last()
        if config_train_coach:
            request.session['already_config'] = True
            last_tracking_log_id = TrackingData.objects.filter(user=request.user, config=config_train_coach).last() # getting None if no data is there
            request.session['last_tracking_log_id'] = last_tracking_log_id.id if last_tracking_log_id is not None else None
            
            if request.session.get('train_stations', None) is None:
                train_details(request, Trains.objects.get(id=config_train_coach.train_id).number)
            object_list = TrainInnerStation.objects.filter(train_id=config_train_coach.train).order_by('order')
            
            ctx = {'config': config_train_coach, 'object_list': object_list, 'led_col_opt': LED_COL_OPT}
            if board_defualt_run_thread is not None and board_defualt_run_thread.is_alive():
                # Set the event to signal the thread to stop
                # stop_event.set()
                # # Wait for the thread to stop
                # board_defualt_run_thread.join()
                # # Reset the event for future use
                # stop_event.clear()
                board_defualt_run_thread_b = False
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
        with open(BOARD_PICKLE_FILE, 'wb') as f:
            pickle.dump(LEDBoard(), f)

        # check if this thread already running then stop this thread first
        if board_train_data_thread is not None and board_train_data_thread.is_alive():
            board_train_data_thread_b = False

        # Check if the thread is not already running
        if board_defualt_run_thread is None or not board_defualt_run_thread.is_alive():
            board_defualt_run_thread = threading.Thread(target=board_run_default, name="BoardDefaultRunThread")
            board_defualt_run_thread_b = True
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
    while board.occupy:
        tm.sleep(1)
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
    cache_init()
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
                    login_info = LoginInfo(user=user)
                    login_info.save()
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
    # ConfigInfo.objects.all().delete()  # Truncate the table associated with ConfigInfo
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect("/login")


def trains(request):
    if request.user.is_authenticated:
        object_list = Trains.objects.all()
        items_per_page = 10
        paginator = Paginator(object_list, items_per_page)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        return render(request, 'inderr/trains.html', context)
    else :
        return redirect('/')

def emit_rpi_data(request, data):
    import socket
    # Define the Raspberry Pi's IP address and port
    # raspberry_pi_ip = '192.168.43.15'  # aman wifi
    #raspberry_pi_ip = '192.168.137.8'
    raspberry_pi_ip = '192.168.31.89'  # madhya airtel
    raspberry_pi_port = 1026
    ack_data = ""
    try:
        f = open("ack.txt", "r")
        ack_data = f.read()
        f.close()
        if ack_data == "":
            train_stations = request.session.get('train_stations')
            train_stations['get_ack'] = ack_data
            print('Ack status:',ack_data)
            train_stations['next_station'] = data['next_station']
            # train_stations['curr_location'] = data['curr_location']
            train_stations['speed'] = data['speed']
            train_stations['late_by'] = data['late_by']
        else:
            train_stations = {}
            train_stations['get_ack'] = ack_data
            train_stations['next_station'] = data['next_station']
            # train_stations['curr_location'] = data['curr_location']
            train_stations['speed'] = data['speed']
            train_stations['late_by'] = data['late_by']

        already_config = request.session.get('already_config', False)
        print('already config is ', already_config)
        if already_config:
            last_tracking_log_id = request.session.get('last_tracking_log_id', None)
            print(last_tracking_log_id)
            if last_tracking_log_id:
                last_tracking_log = TrackingData.objects.get(id = last_tracking_log_id)
                distance_skip = haversine_distance(data['next_station']['curr_lat'], data['next_station']['curr_lon'], last_tracking_log.curr_lat, last_tracking_log.curr_lon)
                print('distance skip is', distance_skip)
        
        next_station = TrackingData(
            name=data['next_station']['name'],
            lat=data['next_station']['lat'],
            lon=data['next_station']['lon'],
            curr_lat=data['next_station']['curr_lat'],
            curr_lon=data['next_station']['curr_lon'],
            order=data['next_station']['order'],
            remaining_distance=data['next_station']['remaining_distance'],
            is_crossed=data['next_station']['is_crossed'],
            actual_arrival_time=datetime.fromisoformat(data['next_station']['actual_arrival_time']) if data['next_station']['actual_arrival_time'] else None,  # actual_arrival_time is False, so we set it to None
            actual_departure_time=datetime.fromisoformat(data['next_station']['actual_departure_time']) if data['next_station']['actual_departure_time'] else None,  # actual_departure_time is False, so we set it to None
            abbr=data['next_station']['abbr'],
            distance=data['next_station']['distance'],
            total_distance=data['next_station']['total_distance'],
            estimate_time=datetime.strptime(data['next_station']['estimate_time'], '%H:%M').time(),
            depart_time=datetime.strptime(data['next_station']['depart_time'], '%H:%M').time(),
            halt_time=data['next_station']['halt_time'],
            total_time_to_reach=datetime.fromisoformat(data['next_station']['total_time_to_reach']) if data['next_station'].get('total_time_to_reach', None) else None,
            instant_distance=data['next_station']['instant_distance'],
            instant_speed=data['next_station']['instant_speed'],
            late_by=data['next_station']['late_by'],
            user = request.user,
            config = ConfigInfo.objects.filter(status=0, user_id=request.user).first(),
        )

        next_station.save()

        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the Raspberry Pi
        client_socket.connect((raspberry_pi_ip, raspberry_pi_port))
        print(train_stations)
        # Serialize the dictionary object using pickle
        serialized_data = pickle.dumps(train_stations)
        # serialized_data = json.dumps(data).encode('utf-8')
        client_socket.send(serialized_data)

        if ack_data == "":
            print('Ack data status in if:',ack_data)
            # Wait for acknowledgment
            ack = client_socket.recv(1024)
            if ack.decode() == "ACK":
                print("Acknowledgment received")
                request.session['get_ack'] = True   
                print('setup ack to true')
                with open("ack.txt", "w") as f:
                    f.write('ACK')
                print('Ack write ok:')
            else:
                print("Error: Acknowledgment not received properly")


        # Close the socket
        client_socket.close()
        return JsonResponse({'success': 'Called Successfully'}, status=200)
    except socket.gaierror as e:
        print({'error': f"An error occurred1: {e}"})
        logger.exception(f"A socket error occurred while trying to connecct with Raspberry PI: {e}")
        return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
        # return f"Socket error: {e}"
    except Exception as e:
        print({'error': f"An error occurred2: {e}"})
        logger.exception(f"An unknown error occurred while trying to connecct with Raspberry PI: {e}")
        return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
        # return f"An error occurred: {e}"

def move_data_to_history():
    # Start an atomic transaction to ensure all operations are completed successfully
    with transaction.atomic():
        # Retrieve all data from the main table
        main_data = TrackingData.objects.all()

        # Create history entries for each record in the main table
        history_entries = []
        for entry in main_data:
            history_entry = TrackingDataHistory(
                name = entry.name,
                lat = entry.lat,
                lon = entry.lon,
                curr_lat = entry.curr_lat,
                curr_lon = entry.curr_lon,
                order = entry.order,
                remaining_distance = entry.remaining_distance,
                is_crossed = entry.is_crossed,
                actual_arrival_time = entry.actual_arrival_time,
                actual_departure_time = entry.actual_departure_time,
                abbr = entry.abbr,
                distance = entry.distance,
                total_distance = entry.total_distance,
                estimate_time = entry.estimate_time,
                depart_time = entry.depart_time,
                halt_time = entry.halt_time,
                total_time_to_reach = entry.total_time_to_reach,
                instant_distance = entry.instant_distance,
                instant_speed = entry.instant_speed,
                late_by = entry.late_by,
                timestamp = entry.timestamp,
                user = entry.user,
                config = entry.config,
            )
            history_entries.append(history_entry)

        # Bulk create the history entries
        TrackingDataHistory.objects.bulk_create(history_entries)

        # Clear the main table
        TrackingData.objects.all().delete()


def do_journy_completed_steps(request, is_completed):
    # Journy is completed doing necessary steps
    # 1.) Logout user
    # 2.) set config to 1
    # 3.) clear/flush cache
    # 4.) move train log data to history table
    # 5.) stop sending data to RPI (logout will redirected to the login page so, no more data will send)
    if is_completed :
        # clear/flush cache
        cache.clear()
        cache.set('is_cache_setup', False)

        # set config to 1
        config_obj = ConfigInfo.objects.filter(status=0).last()
        if config_obj:
            config_obj.status = True
            config_obj.save()

        # move train log data to the history table
        move_data_to_history()

        # logout 
        # logout(request)
        # or 
        user_logout(request)


def train_details(request, train_number):
    if request.user.is_authenticated:
        check_already_config(request)
        train = Trains.objects.get(number=train_number)
        object_list = TrainInnerStation.objects.filter(train_id=train).order_by('order')
        places = Temp.objects.all()

        next_stations, gps_obj, stations, is_journy_completed = get_next_station(train.id)
        current_time = datetime.now().time()
        # Convert the current time to a datetime object with today's date
        current_datetime = datetime.combine(datetime.today(), current_time)
        late_by_min = (current_datetime - datetime.combine(datetime.today(), object_list[0].departs)).total_seconds() / 60
        late_by = 0 if late_by_min < 0 else round(late_by_min, 0)
        # context = {'train': train, 'object_list':object_list, 'places':places, 'curr_location':get_coords(), 'next_stations':next_stations }
        # stations = []
        # total_distance = 0
        # for station in object_list:
        #     if station.distance: total_distance +=station.distance
        #     stations.append({
        #         'name': station.station_id.name,
        #         'abbr': station.station_id.code,
        #         'distance': station.distance,
        #         'total_distance': total_distance,
        #         'order': station.order,
        #         'estimate_time': station.arrives.strftime('%H:%M') if station.arrives is not None else None,
        #         'delay_time': station.departs.strftime('%H:%M') if station.departs is not None else None,
        #         'lat': str(station.station_id.lat),
        #         'lon': str(station.station_id.lon),
        #         'halt_time': station.halt_time
        #     })
        res_data = {
            'train': {
                'name': train.name,
                'number': train.number,
                'from_station': train.from_station.name,
                'to_station': train.to_station.name
            },
            'stations': stations,
        }
        request.session['train_stations'] = res_data
        request.session['get_ack'] = False
        print('get_ack set to false')
        # return render(request, 'inderr/train-details.html', context)
        
        
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
    return JsonResponse(data,safe=False)

def get_lat_lon2(request): # May include more arguments depending on URL parameters
    # Get data from the database - Ex. Model.object.get(...)
    if request.method == 'POST':
        details = json.load(request)['details']
        place = Temp.objects.get(name=details['place_name'])
        stop_stations = TrainInnerStation.objects.filter(train_id=details['train_id']).order_by('order')

        stop_list = []
        for stations in stop_stations:
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
        return JsonResponse(data,safe=False)

    return JsonResponse({'error': 'Method not allowed'}, status=403)

def send_data_rsp(request):
    if request.method == 'POST':
        # this data variable contains next_staiton {'next_station': {'name': 'Saugor', 'lat': '23.847723', 'lon': '78.744192', 'order': 7, 'distance': 14.974075925058397}} 
        data = json.load(request)['data']
        print(data)
        print('aman')
        # data['curr_location'] = get_coords()
        data['speed'] = 0
        data['late_by'] = 0
        return emit_rpi_data(request, data)
    else:
        return JsonResponse({'error': 'Method not allowed', 'request_method': request.method}, status=403)
    

def get_updated_info(request):
    if request.user.is_authenticated:
        cache_init()
        check_already_config(request)
        if request.method == 'POST':
            details = json.load(request)['details']
            train_id = details['train_id']
            data, gps_obj, stations, is_journy_completed = get_next_station(train_id)
            if is_journy_completed:
                do_journy_completed_steps(request, is_journy_completed)
                return JsonResponse({'error': 'Method not allowed'}, status=403)

            return JsonResponse({'success': 'Called Successfully', 'data': data}, status=200)
        return JsonResponse({'error': 'Method not allowed'}, status=403)
    else :
        return redirect('/')

def config_train_and_coach(request):
    cache_init()
    check_already_config(request)
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ConfigInfoForm(request.POST)
            if form.is_valid():
                train = form.cleaned_data['train']
                train_details(request, train.number)
                with open("ack.txt", "w") as f:
                    pass  # This will open the file and immediately close it, effectively removing its contents
                config_info = form.save(commit=False)
                config_info.user_id = request.user
                config_info.save()
                return redirect('/')  # Redirect to success page after form submission
        else:
            form = ConfigInfoForm()
        trains = Trains.objects.all()  # Get all trains for dropdown
        already_config = ConfigInfo.objects.filter(status=0, user_id=request.user).last()
        if already_config:
            return redirect('/')
        else:
            request.session['already_config'] = False
            return render(request, 'inderr/config_info_form.html', {'form': form, 'trains': trains})
    else :
        return redirect('/')


def change_led_col_speed(request, led_col):
    cache_init()
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