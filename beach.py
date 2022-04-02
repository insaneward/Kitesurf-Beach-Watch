from curses.panel import top_panel
from math import degrees
from time import sleep
from xmlrpc.client import NOT_WELLFORMED_ERROR

from pygame import CONTROLLER_BUTTON_LEFTSTICK
from weather import Weather
from tide import Tide

from beachfuncs import *

class Beach (Tide, Weather):
    # Constructor to load the beach data.
    def __init__ (self, beach, api, coords):
        self.forecastSurface = pygame.Surface((widgetWidth * 5, widgetHeight))
        self.name           = beach['name']
        self.long           = beach['lon']
        self.lat            = beach['lat']
        self.wind_direction = beach['wind_direction']
        self.weather        = Weather(self.lat, self.long, api)
        self.tide           = Tide(beach['tide_station'], beach['tide_wind'])
        self.timezone       = ""
        self.tzoffset       = 0
        self.kiteable       = False
        self.kite           = 0
        self.timetokite     = 0
        self.forecastPos    = coords
        
        print (f'Loaded Beach data: {self.name}, Coords: ({self.long:.2f}, {self.lat:.2f}) Wind range: {self.wind_direction}')

    def getKitetime (self):
        if self.kiteable:
            return self.timetokite
        else:
            return 31536000
    
    def getWeatherForecast(self):
        #self.weather.getWeatherForecast(self.name)
        self.weather.get5WeatherForecast(self.name)
        #self.timezone, self.tzoffset = self.weather.getTimeZone()

    def printWeatherForecast (self):
        if DEBUG:
            self.weather.printWeatherForecast (self.name)

    def getTideForecast(self):
        self.tide.getTideForecast(self.name)

    def printTideForecast(self):
        if DEBUG:
            self.tide.printTides ()

#    def setTimezone (self, timezone, tzoffset):
#        self.timezone = timezone
#        self.tzoffset = tzoffset

    def printBeach (self): 
        print (f'Beach: {self.name}, ({self.long},{self.lat:}), {self.timezone} {self.tzoffset}')
        self.tide.printTides ()

    def renderBeachPG (self, currentTimeZone, currentOffset):
        timenow = getEpochTime()
        timenow -= (currentOffset - self.tzoffset)
        if timenow % 2:
            seperator = ':'
        else:
            seperator = ' '
        timenow = convertEpochTime (timenow)
    
        
        return f'{timenow.tm_hour:02d}{seperator}{timenow.tm_min:02d} {self.name}'
        

    def renderBeachStatusPG (self):
        if self.kiteable:
            return f'Kite {deltaToString(self.kiteforecast.time - getEpochTime())}',f'{self.kite.make} {self.kite.model} {self.kite.size}m'
        else:
            return 'No Kiting',''
    
    def renderCurrentWeatherPG (self):
        return self.weather.renderCurrentWeatherPG()
    
    def renderSummary (self, font, width, currentTimezone, currentOffset):
        self.nameSurface = font.render (self.renderBeachPG(currentTimezone, currentOffset), True, (255,255,0))  

        kitable, kite = self.renderBeachStatusPG()

        self.statusSurface = font.render (kitable, True, (255,255,0))
        self.statusKiteSurface = font.render (kitable + kite, True, (255,255,0))

        self.nameRect = self.nameSurface.get_rect()
        self.statusRect =  self.statusSurface.get_rect()
        self.statusKiteRect = self.statusKiteSurface.get_rect()

        if kite != '':
            self.scrollStatus = True
            self.scrollSpeed = 5
            self.scrollPause = 0
            self.scrollPos = 0
        else:
            self.scrollStatus = False

    def blitSummary (self, surface, scale, width, row):
        surface.blit(self.nameSurface, (0,row)) 


        if self.scrollStatus:
            surface.blit(self.kiteforecast.surfaceForecast, (0,row + rowHeight))
            clipRect = (self.nameRect.width + 10 ,row,width,self.statusRect.height + row)
            #surface.set_clip(clipRect)

            surface.blit(self.statusKiteSurface, (width - (self.statusRect.width + 10) - self.scrollPos, row))

            if self.scrollPos == 0 and self.scrollPause < 50:
                self.scrollPause += 1
                self.scrollPos = 0
            else:
                self.scrollPause = 0
                self.scrollPos += self.scrollSpeed
                if self.scrollPos >= self.statusKiteRect.width + self.statusRect.width:
                    self.scrollPos = 0
                    

            #surface.set_clip(None)
        else:
            surface.blit(self.statusSurface, (width - self.statusRect.width -10, (row))) 

    def checkKitingConditions(self, kiteData):

        for forecast in self.weather.forecast:
            # Mark wheter a forecast is kitable

            #Check whether it's day or night
            if forecast.pod == 'n':
                continue

            # Check the wind direction is right
            if (self.wind_direction [0] < self.wind_direction[1]):
                if (forecast.Winddeg <= self.wind_direction[0]) or (forecast.Winddeg >= self.wind_direction[1]):
                    continue

            else:
                delta = 360 - self.wind_direction[0]
                if ((forecast.Winddeg+delta) >= (self.wind_direction[1]+delta)):
                    continue
                
            # Rain?
            # Wind Speed
            forecast.kiteable = True
            print (f'{forecast.Winddeg} ({self.wind_direction[0]},{self.wind_direction[1]})')

            #

    def renderForecast (self, icons):

        self.forecastSurface.fill(background)
        nameStr = fontSmall.render (self.name, True, (255,255,0)) 
        nameRect = nameStr.get_rect()
        epochNow = getEpochTime()
        tileWidth = int (widgetWidth / 8)
 

        for numdays in range (0,forecastDays):

            timeNow = epochToTS (epochNow)

            tempStr = dateFromTS(timeNow)
            dateStr = fontSmall.render (tempStr, True, (255,255,0))
            dateRect = dateStr.get_rect()

            self.forecastSurface.blit (nameStr, (numdays * widgetWidth,0)) 
            x = (numdays+1) * widgetWidth - dateRect.width
            self.forecastSurface.blit (dateStr,(x, 0))

            todaysForecast = self.weather.getDaysForecast(timeNow)
            count = 0
            for forecast in todaysForecast:
                for icon in icons:
                    if icon.id == forecast.Id:
                        break
                        
                tile = pygame.Rect((count * tileWidth) + (widgetWidth * numdays), 
                                   nameRect.height + 2, 
                                   tileWidth, 
                                   widgetHeight - nameRect.height  -2)
          
                timeStr         = f'{forecast.timeTS.tm_hour:02d}:{forecast.timeTS.tm_min:02d}'
                timeSurface     = fontSmaller.render (timeStr, True, (255,255,0)) 
                timeRect        = timeSurface.get_rect(midtop=(tile.centerx,tile.top))

                self.forecastSurface.blit (timeSurface, timeRect)

                charRect = icon.getCharRect()
                charRect.midtop = (tile.centerx,timeRect.bottom+(1*widgetScale))
                height = icon.showChar(self.forecastSurface,charRect)

                # Time, Temp, Wind, Direction, Gust, Rain

                tempStr         = f'{forecast.temp}°C'
                tempSurface     = fontSmaller.render (tempStr, True, (255,255,0)) 
                tempRect        = tempSurface.get_rect(midtop = (tile.centerx,charRect.bottom - (2*widgetScale)))
                self.forecastSurface.blit (tempSurface, tempRect)


                windStr         = f'{forecast.Windspeed}-{forecast.Windgust}kt'
                windSurface     = fontSmaller.render (windStr, True, (255,255,0)) 
                windRect        = windSurface.get_rect(midtop=(tile.centerx,tempRect.bottom+(1*widgetScale)))
                self.forecastSurface.blit (windSurface, windRect)

                windDirStr         = f'{forecast.Winddirection}'
                windDirSurface     = fontSmaller.render (windDirStr, True, (255,255,0)) 
                windDirRect        = windDirSurface.get_rect(midtop=(tile.centerx,windRect.bottom+(1*widgetScale)))
                self.forecastSurface.blit (windDirSurface, windDirRect)

                rainStr         = f'{forecast.rain}'
                rainSurface     = fontSmaller.render (rainStr, True, (255,255,0)) 

                count += 1

            epochNow += 86400
        #segments:
        #Time, Icon, Wind (gust), direction,  rain, temperature
        
        return

    def displayForecast (self, surface, day=0):
        surface.blit (self.forecastSurface, self.forecastPos)
            
    def updateStatus (self, kites):
        self.kiteable = False
        self.kite = None
        self.kiteforecast = None

        timeNow = getEpochTime()
        for kite in kites:
            windrange, sweetspot  = kite.getWindrange()

            kiteforecast = self.weather.checkForecast (self.name, windrange, sweetspot, self.wind_direction)
            if kiteforecast and (self.kite == None or ((kiteforecast.time - timeNow) < self.timetokite)):

                
                self.kite = kite
                self.timetokite = kiteforecast.time - timeNow
                self.kiteable = True
                self.kiteforecast = kiteforecast
                if DEBUG:
                    print (f' {self.name} kiteable on {kite.getText()} at {kiteforecast.getText()} ')
