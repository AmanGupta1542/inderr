from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.http import JsonResponse
import json
from django.db.models import Q

from .forms import UserLogin, UserImage
from .models import Trains, TrainInnerStation, UploadImage, Temp

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
        return render(request=request, template_name="inderr/login.html", context={"login_form":form})


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

def train_details(request, train_number):
    if request.user.is_authenticated:
        train = Trains.objects.get(number=train_number)
        object_list = TrainInnerStation.objects.filter(train_id=train).order_by('order')
        places = Temp.objects.all()
        context = {'train': train, 'object_list':object_list, 'places':places}
        # print(object_list)
        return render(request, 'inderr/train-details.html', context)
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
        # Define the Raspberry Pi's IP address and port
        # raspberry_pi_ip = '192.168.43.15'  # aman wifi
        #raspberry_pi_ip = '192.168.137.8'
        raspberry_pi_ip = '192.168.1.15'  # madhya airtel
        raspberry_pi_port = 1026
        try:
            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the Raspberry Pi
            client_socket.connect((raspberry_pi_ip, raspberry_pi_port))

            # Send data to the Raspberry Pi
            # data = "Hello, Raspberry Pi!"
            data = data['next_stations']
            client_socket.send(data.encode('utf-8'))
            # Close the socket
            client_socket.close()
            return JsonResponse({'success': 'Called Successfully'}, status=200)
        except socket.gaierror as e:
            return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
            # return f"Socket error: {e}"
        except Exception as e:
            return JsonResponse({'error': f"An error occurred: {e}"}, status=500)
            # return f"An error occurred: {e}"
    return JsonResponse({'error': 'Method not allowed'}, status=403)