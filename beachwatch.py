# importing requests and json
from asyncio.base_subprocess import WriteSubprocessPipeProto
from re import X
from tkinter import Canvas
from turtle import screensize, setundobuffer

import json

from datetime import timedelta
from timeloop import Timeloop
from datetime import datetime
from sys import exit

import pygame
from pygame.locals import *

from urllib.request import urlopen

from beach import Beach
#from tide import Tide
from beachfuncs import *


class Icon:
    #Class scope font


    def __init__ (self, data, debug):
        self.id = data["code"]
        self.shortdesc = data['shortdesc']
        self.desc = data['longdesc']

        self.dayChar = fontWeather.render (data['daychar'], True, (255,255,0)) 
        self.dayCharRect = self.dayChar.get_rect()
        self.nightChar = fontWeather.render (data['nightchar'], True, (255,255,0)) 
        self.nighCharRect = self.nightChar.get_rect()
    
    def showChar (self, surface, charRect):
        surface.blit(self.dayChar, charRect)

    def getCharRect (self):
        return self.dayCharRect



class Kite:
    def __init__(self, make, model, size, windrange, debug):
        self.make = make
        self.model = model
        self.size = size
        self.windrange = windrange
        self.sweetspot = int((windrange[0] + windrange[1])/2)
        if debug:
            print (f'Loaded Kite data: {self.make}, {self.model}, {self.size}m Wind range: {self.windrange}')

    def getText (self):
        return f'{self.make} {self.model} {self.size}m'
 
    def getWindrange (self):
        return self.windrange, self.sweetspot

def sortKiteable (beach):
    return beach.getKitetime ()

def loadConfig():
    with open('weather.json', 'r') as jsonConfig:
        data = json.load(jsonConfig)

    with open('icons.json', 'r') as jsonIcons:
        icons = json.load(jsonIcons)

    return data, icons

def renderTimePi():
    strTime = epochToStr (getEpochTime())
    rawTime = datetime.now()

    return strTime

def renderDateTimePi():
    rawTime = datetime.now()
    strTime = rawTime.strftime("%H:%M:%S")
    strDate = rawTime.strftime("%A-%d-%B-%Y")

    return strTime, strDate


configData, iconData = loadConfig()
numBeaches = len(configData['beaches'])
screenMatrix = (forecastDays+1,max(numBeaches, 1 + (int(numBeaches/2) + numBeaches %2)))

    
screenSequence = []
for loop in range(numBeaches):
    screenSequence.extend(list(range (0,1+(int(numBeaches/2) + numBeaches %2))))
    screenSequence.extend(list(range(screenMatrix[1] + loop,(forecastDays+1) * screenMatrix[1] + loop,screenMatrix[1])))


#Canvas
#    0.  TIME                , 8.  FORECAST BEACH 1
#    1.  KITEABLE BEACH 1/2  , 9.  FORECAST BEACH 2
#    2.  KITEABlE BEACH 3/4  , 10. FORECAST BEACH 3
#    3.  KITEABlE BEACH 5/6  , 11. FORECAST BEACH 4
#    4.  KITEABlE BEACH 7/8  , 12. FORECAST BEACH 5
#    5.                        13. FORECAST BEACH 6
#    6.                        14. FORECAST BEACH 7
#    7.                        15. FORECAST BEACH 8


canvas = pygame.Surface((widgetWidth * screenMatrix[0], widgetHeight * screenMatrix[1]))
currentScreen = 0

if DEBUG:
    screen = pygame.display.set_mode((widgetWidth * screenMatrix[0], widgetHeight * screenMatrix[1]))
else:
    screen = pygame.display.set_mode((widgetWidth, widgetHeight))

clock = pygame.time.Clock()


for icon in iconData['icons']:
    icons.append(Icon (icon, DEBUG))

for kite in configData['kites']:
    aKite = Kite(kite['Brand'],kite['Type'],kite['Size'],kite['Range'], DEBUG)
    kiteData.append(aKite)

for count in range (0,len(configData['beaches'])):
    aBeach = Beach(configData['beaches'][count],configData['weatherAPI'], (widgetWidth,count * widgetHeight))
    aBeach.getTideForecast()
    aBeach.getWeatherForecast()
    aBeach.checkKitingConditions(kiteData)
#    aBeach.printWeatherForecast()
#    aBeach.printTideForecast()
    aBeach.updateStatus(kiteData)
    aBeach.renderSummary (font, widgetWidth, timezone, timeoffset)
    aBeach.renderForecast (icons)
    beachData.append(aBeach)

# Now sort the beach data into first kiteable
beachData.sort(key=sortKiteable)
timeNow = timeSinceScreenChange = timeSinceConfigRefresh = timeSinceForecastRefresh = timeSinceTideRefresh = getEpochTime()

currentRect = (0,0,widgetWidth, widgetHeight)

while True:
    pygame.display.update() 
    canvas.fill(background)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    clock.tick(25)

    if(timeNow - timeSinceScreenChange >= 5):
        print ("Change Screen")
        currentScreen += 1
        currentScreen %= len(screenSequence)
        x = int(screenSequence[currentScreen] / screenMatrix[1])
        y = screenSequence[currentScreen] % screenMatrix[1]
        currentRect = (x * widgetWidth, y * widgetHeight, widgetWidth, widgetHeight)
        

        # Sequence: 
        # Cycle through main screens
        # Cycle through forecast for beach
        # Cycle through main screen
        # Cycle through next forecasts
        
        #stage: 1 main screen
        #stage: 2 forecastDay


        timeSinceScreenChange = timeNow

    if(timeNow - timeSinceConfigRefresh >= configData["configRefreshTime"]):
        configData2, iconData2 = loadConfig()
        if DEBUG:
            print ("Reloading Config: ", end="")

        # Crude check to see if the config is the same or not
        if configData == configData2:
            if DEBUG:
                print ("Unchanged")
        else:
            # in the case that that data has changed, we should;
            #   Reload all the kites
            #   Reload all the beaches
            #   Get the tide forecasts
            #   Get the weather forcasts
            #   Work out what is kiteable
            configData = configData2

            if DEBUG:
                print ("Changed")

        timeSinceConfigRefresh = timeNow

    # Most weather forecasts change every hour
    if(timeNow - timeSinceForecastRefresh >= configData["forecastRefreshTime"]):
        #   Get the weather forcasts
        #   Work out what is kiteable

        if DEBUG:
            print ("Refresh forecast")


        for beach in beachData:
            beach.getWeatherForecast()
            beach.updateStatus(kiteData)
            beach.renderSummary (font, widgetWidth * widgetScale, timezone, timeoffset)

        beachData.sort(key=sortKiteable)
        timeSinceForecastRefresh = timeNow

    if(timeNow - timeSinceTideRefresh >= configData["tideRefreshTime"]):
        if DEBUG:
            print ("Refresh Tide")
        beach.getTideForecast()
        timeSinceTideRefresh = timeNow

    # Update times (time @ beach, and kiteable tims)
    for beach in beachData:
        beach.renderSummary (font, widgetWidth, timezone, timeoffset)       
        beach.displayForecast (canvas,0)

    # Time & Date in first Canvas
    timeStr, dateStr = renderDateTimePi ()
    timeSurface = fontTime.render(timeStr, True, (255,255,0))
    timeRect = timeSurface.get_rect()
    dateSurface = fontDate.render(dateStr, True, (255,255,0))
    dateRect = dateSurface.get_rect()
    canvas.blit(timeSurface,((widgetWidth - timeRect.width)/2, 10))
    canvas.blit(dateSurface,((widgetWidth - dateRect.width)/2, 50))

    for row in range(0,len(beachData)):
        beachData[row].blitSummary (canvas, widgetScale, widgetWidth, widgetHeight + (row * rowHeight * 2))

    timeNow = getEpochTime ()
    screen.blit (canvas, (0,0), area=currentRect)

    if DEBUG:
        #Draw middle line
        pygame.draw.line(screen,(255,0,0),(widgetWidth,0),(widgetWidth,(widgetHeight * (len(beachData)+1))))
        pygame.draw.line(screen,(255,0,0),(widgetWidth*2,0),(widgetWidth*2,(widgetHeight * (len(beachData)+1))))
        pygame.draw.line(screen,(255,0,0),(widgetWidth*3,0),(widgetWidth*3,(widgetHeight * (len(beachData)+1))))
        pygame.draw.line(screen,(255,0,0),(widgetWidth*4,0),(widgetWidth*4,(widgetHeight * (len(beachData)+1))))
        pygame.draw.line(screen,(255,0,0),(widgetWidth*5,0),(widgetWidth*5,(widgetHeight * (len(beachData)+1))))

        #Draw Horizontal lines
        for x in range (1,len(beachData)+1):
            pygame.draw.line(screen,(255,0,0),(0,widgetHeight * x),(widgetWidth * 6,widgetHeight * x))

        pygame.draw.rect(screen,(255,255,255), currentRect, width=1)
       
pygame.quit()

