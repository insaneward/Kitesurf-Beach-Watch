
#from logging import DEBUG
from pkg_resources import yield_lines
import requests, json
from beachfuncs import *

class Forecast:
    def __init__ (self, data, tzoffset):
        self.time          = data['dt']+tzoffset
        self.timeTS        = epochToTS(self.time)

        self.temp          = int(data['main']['temp']-273.15)
        self.feels_like    = int(data['main']['feels_like']-273.15)
        self.temp_min      = int(data['main']['temp_min']-273.15)
        self.temp_max      = int(data['main']['temp_max']-273.15)
        self.pressure      = data['main']['pressure']
        self.sea_level     = data['main']['sea_level']
        self.grnd_level    = data['main']['grnd_level']
        self.humidity      = data['main']['humidity']
        self.visibility    = data['visibility']
        self.pop           = data['pop']
        self.pod           = data['sys']['pod']

        self.Main          = data['weather'][0]['main']
        self.Id            = data['weather'][0]['id']
        self.Description   = data['weather'][0]['description']
        self.Icon          = data['weather'][0]['icon']

        self.Clouds        = data['clouds']['all']

        self.Windspeed     = int(data['wind']['speed']*1.94384)
        self.Winddirection = windDirectionFromDegrees(data['wind']['deg'])
        self.Winddeg       = data['wind']['deg']
        self.Windgust      = int(data['wind']['gust']*1.94384)

        if 'rain' in data:
            self.rain       = data['rain']['3h']
        else:
            self.rain       = 0
        if 'snow' in data:
            self.snow       = data['snow']['3h']
        else:
            self.snow       = 0;

        self.kiteable       = False
        self.kite           = None


    def _init_ (self, tzoffset, data, forecasttype, sunrise = None, sunset = None):
        self.time          = data['dt']+tzoffset
        self.timeTS        = epochToTS(self.time)
        self.Humidity      = data['humidity']
        self.Pressure      = data['pressure']
        self.Windspeed     = data['wind_speed']*1.94384
        self.Winddirection = windDirectionFromDegrees(data['wind_deg'])
        self.Winddeg       = data['wind_deg']

        self.Uvi           = data['uvi']
        self.Clouds        = data['clouds']


        # Not always sent on Now
        if forecasttype != 'current':
            self.Pop           = data['pop']
            self.Windgust      = data['wind_gust'] *1.94384
        else:
            self.Pop = None
            self.Windgust      = self.Windspeed


        #Not sent on hourly
        if forecasttype != 'hourly':
            self.sunrise    = data['sunrise']+tzoffset
            self.sunset     = data['sunset']+tzoffset
        else:
            self.sunrise    = sunrise
            self.sunset     = sunset

        if forecasttype == 'daily': 
            self.Temp      = data['temp']['day']-273.15
            self.Visibility= None
        else:
            self.Temp      = data['temp']-273.15
            self.Visibility= data['visibility']

        weather            = data['weather'][0]
        self.Main          = weather['main']
        self.Id            = weather['id']
        self.Description   = weather['description']
        self.Icon          = weather['icon']

    def getText (self):
        return f'{epochToStr(self.time)}, {int(self.Windspeed)}knts, {windDirectionFromDegrees(self.Winddeg)}'

    def printForecast (self, name):
        print (f'{name}, {epochToStr(self.time)}, {int(self.Windspeed)}knts, {windDirectionFromDegrees(self.Winddeg)} Kite: {self.kiteable}') 

    

class Weather:
    def __init__ (self,lat, long, api):
        self.forecast = []
        self.current = []

        self.weather_url = "https://api.openweathermap.org/data/2.5/onecall?exclude=minutely&lat=" + str(lat) + "&lon=" + str(long) + "&appid=" + api
        self.weather5_url = "https://api.openweathermap.org/data/2.5/forecast?lat=" + str(lat) + "&lon=" + str(long) + "&appid=" + api

#https://api.openweathermap.org/data/2.5/onecall?exclude=minutely&lat=-3.06378&lon=40.17283&appid=5060ac833dc83e4e2886f55a8a89dd04

    def getWeatherForecast (self, name):
        filename = f'data/{name} - weather.json'
        if DEMODATA:
            with open(filename, 'r') as jsonConfig:
                data = json.load(jsonConfig)
            if DEBUG: 
                print ("OpenWeather demo data loaded")
        else:
            # HTTP request
            response = requests.get(self.weather_url)
            # checking the status code of the request


            if response.status_code != 200:
                # showing the error message
                print("Error in the HTTP request", self.weather_url)
                return
            if DEBUG:
                print ("OpenWeather, data obtained")
            data = response.json()
            
            with open(filename, 'w') as f:
                f.write(json.dumps(data, indent=2))
                f.close()

        # getting the main dict block
        self.timezone, self.tzoffset = data['timezone'], int(data['timezone_offset'])

        self.forecast.append(Forecast(self.tzoffset,data['current'], 'current'))
        for forecast in data['hourly']:
            self.forecast.append(Forecast(self.tzoffset,forecast, 'hourly', data['current']['sunrise'],data['current']['sunset']))

        for forecast in data['daily']:
            self.forecast.append(Forecast(self.tzoffset, forecast, 'daily'))
    
    def get5WeatherForecast (self, name):
        filename = f'data/{name} - weather 5.json'
        if DEMODATA:
            with open(filename, 'r') as jsonConfig:
                data = json.load(jsonConfig)
            if DEBUG:
                print ("OpenWeather demo data loaded")
        else:
            # HTTP request
            response = requests.get(self.weather5_url)
            # checking the status code of the request


            if response.status_code != 200:
                # showing the error message
                print("Error in the HTTP request", self.weather5_url)
                return
            if DEBUG:
                print ("OpenWeather - 5 day forecast, data obtained")
            data = response.json()
            
            with open(filename, 'w') as f:
                f.write(json.dumps(data, indent=2))
                f.close()


        city = data['city']
        self.tzoffset =  data['city']['timezone']
        self.sunrise  =  data['city']['sunrise']
        self.sunset   =  data['city']['sunset']

        for period in data['list']:
            self.forecast.append(Forecast(period,self.tzoffset))

        # getting the main dict block
        #self.timezone, self.tzoffset = data['timezone'], int(data['timezone_offset'])

        #self.forecast.append(Forecast(self.tzoffset,data['current'], 'current'))
        #for forecast in data['hourly']:
        #    self.forecast.append(Forecast(self.tzoffset,forecast, 'hourly', data['current']['sunrise'],data['current']['sunset']))

        #for forecast in data['daily']:
        #    self.forecast.append(Forecast(self.tzoffset, forecast, 'daily'))

    def getTimeZone (self):
        return self.timezone, self.tzoffset

    def printWeatherForecast(self, name):
        for forecast in self.forecast:
            forecast.printForecast(name)

    def getDaysForecast (self, dayTS):
        print (dayTS)
        for forecast in self.forecast:
            forecastTS = time.gmtime(forecast.time)
            if dayTS.tm_yday == forecastTS.tm_yday:
                yield forecast
            elif (forecastTS.tm_yday > dayTS.tm_yday):
                return


    def checkForecast (self, name, windrange, sweetspot, direction):
        timeNow = getEpochTime()
        for forecast in self.forecast:
 
            if forecast.kiteable == False:
                continue

            #Check the wind speed first
            if (forecast.Windspeed > windrange[0] and forecast.Windspeed < windrange[1]):

                # Is it in the future
                if (forecast.time - timeNow > 0):
                    #Should check the high tide forcast
                    #render a forecast line so we don't need to do it again, and get rect
                    forecast.forecastText = f'{windDirectionFromDegrees(forecast.Winddeg)} {int(forecast.Windspeed)} {int(forecast.Windgust)} {epochToStr(forecast.time)} {forecast.pop}%'
                    forecast.surfaceForecast = fontSmall.render (forecast.forecastText, True, (255,255,0))
                    forecast.surfaceForecastRect = forecast.surfaceForecast.get_rect()
                    return forecast

        return None

    def renderCurrentWeatherPG (self):
        return f'{self.forecast[0].currentTemp} {self.forecast[0].currentWindspeed} {self.forecast[0].currentWinddirection}'

        #print(f"Time           : {time.asctime(time.gmtime(main['dt']+self.tzoffset))}")
        #print(f"Wind Speed     : {main['wind_speed']*1.94384:2.1f} Knots")
        #print(f"Wind Gust      : {main['wind_gust']}")
        #print(f"Wind Direction : {windDirectionFromDegrees(main['wind_deg'])}, ({main['wind_deg']}°)")
        #print(f"Clouds         : {main['clouds']}%")
 #       print(f"Temperature    : {main['temp']-273.15:03.2f}°c")
