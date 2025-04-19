from django.shortcuts import render, redirect
import requests
from .models import City
from .forms import CityForm

# OpenWeatherMap API key
API_KEY = 'bce156dc1f3c8f868dd37dc4c09c1cbf'
url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=' + API_KEY

def index(request):
    err_msg = ''
    message = ''
    message_class = ''

    if request.method == 'POST':
        form = CityForm(request.POST)
        if form.is_valid():
            new_city = form.cleaned_data['name']
            existing_city_count = City.objects.filter(name__iexact=new_city).count()

            if existing_city_count == 0:
                r = requests.get(url.format(new_city)).json()
                if r.get('cod') == 200:
                    form.save()
                else:
                    err_msg = 'City does not exist!'
            else:
                err_msg = 'City already exists!'

        if err_msg:
            message = err_msg
            message_class = 'is-danger'
        else:
            message = 'City added successfully!'
            message_class = 'is-success'

    form = CityForm()
    cities = City.objects.all()
    weather_data = []

    for city in cities:
        r = requests.get(url.format(city.name)).json()
        if r.get('cod') == 200:
            city_weather = {
                'city': city.name,
                'temperature': r['main']['temp'],
                'description': r['weather'][0]['description'],
                'icon': r['weather'][0]['icon'],
            }
            weather_data.append(city_weather)

    context = {
        'weather_data': weather_data,
        'form': form,
        'message': message,
        'message_class': message_class
    }

    return render(request, 'weather/weather.html', context)

def delete_city(request, city_name):
    City.objects.filter(name=city_name).delete()
    return redirect('home')
