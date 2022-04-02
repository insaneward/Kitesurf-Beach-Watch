# importing requests and json
from asyncio.base_subprocess import WriteSubprocessPipeProto
from re import X
from tkinter import Canvas
from turtle import setundobuffer

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

        self.nightchar = data['daychar']
        fname = data['dayicon']
        self.icon = pygame.image.load(fname)
        self.iconRect = self.icon.get_rect()

        if self.iconRect.width > (widgetWidth/9):
            newheight = self.iconRect.height * ((widgetWidth/9) /  self.iconRect.width)
            self.icon = pygame.transform.scale(self.icon, (int(widgetWidth/9),int(newheight)))
            self.iconRect = self.icon.get_rect()

        if 'nighticon' in data:
            fname = data['nighticon']
            self.nighticon = pygame.image.load(fname)

        else:
            self.nighticon = None

    def showIcon (self, surface, x, y):
        surface.blit(self.icon, (x, y))
    
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

def renderDestinationPi(departure):
    departureTime = departure["aimed_departure_time"]
    destinationName = departure["destination_name"]
    return f"{departureTime}  {destinationName}"

def renderServiceStatusPi(departure):
    return "On time" if departure["aimed_departure_time"] == departure[
            "expected_departure_time"] else departure["expected_departure_time"]

def renderCallingAtPi():
    return "Calling at: "

def renderServiceDetailsPi():
    return "This train is formed of 10 coaches"

def renderSWRPi ():
    return "SWR"

def renderTimePi():
    strTime = epochToStr (getEpochTime())
    rawTime = datetime.now()
 #   strTime = str(rawTime)
 #   hour, minute, second = strTime.split('.')[0].split(':')

    #return "{}:{}:{}".format(rawTime.hour, rawTime.minute, rawTime.second)
    return strTime

 #   draw.text((width - 84) / 2, 0)(, text="{}:{}".format(hour, minute),
 #             font=fontBoldLarge, fill="yellow")
 #   draw.text((((width - 84) / 2) + w1, 3), text=":{}".format(second),
 #             font=fontBold, fill="yellow")

def renderDateTimePi():
    rawTime = datetime.now()
    strTime = rawTime.strftime("%H:%M:%S")
    strDate = rawTime.strftime("%A-%d-%B-%Y")

    return strTime, strDate


def drawSignagePiGame(surface, width, height, data, scale):
    global RenderCount, pauseCount

    #Draw rotated arrow
    #if data[0].kiteable:
    #    arrowRect=arrowImg.get_rect()
    #    rotArrowImg = pygame.transform.rotate(arrowImg, data[0].kiteforecast.Winddeg)
    #    rotArrowRect = rotArrowImg.get_rect()
    #    rotArrowRect.center = (arrowRect.centerx + 100, arrowRect.centery+10)
    #    screen.blit(rotArrowImg, rotArrowRect)
 

    #rowTwoASurface = font.render (data[1].renderBeachPG(), True, (255,255,0))  
 #   stationsAt = renderStationsPi(", ".join(firstDepartureDestinations))
 #   stationsAt = ", ".join(firstDepartureDestinations)
    #rowTwoBSurface = font.render (data[1].renderBeachStatusPG(), True, (255,255,0))
    #rowTwoBRect = rowTwoBSurface.get_rect()

    #screen.blit(rowOneASurface, (0,0)) 
    #screen.blit(rowOneBSurface, (width - rowOneBRect.width - (5 * scale), 0)) 
    #screen.blit(rowTwoASurface, (0,16 * scale)) 
    #screen.blit(rowTwoBSurface, (width - rowTwoBRect.width - (5 * scale), 16 * scale))



    if False:
        clipRect = (callingWidth,16 * scale,width * scale,rowTwoBRect.height)
        screen.set_clip(clipRect)


        screen.blit(rowTwoBSurface, (callingWidth - RenderCount, 32))  

        if RenderCount == 0 and pauseCount < 120:
            pauseCount += 1

            RenderCount = 0
        else:
            pauseCount = 0
            RenderCount += 2
            if RenderCount >= rowTwoBRect.width:
                RenderCount = 0

        screen.set_clip(None)

    # Time & Date in first Canvas
    timeStr, dateStr = renderDateTimePi ()
    timeSurface = fontTime.render(timeStr, True, (255,255,0))
    timeRect = timeSurface.get_rect()
    dateSurface = fontDate.render(dateStr, True, (255,255,0))
    dateRect = dateSurface.get_rect()
    surface.blit(timeSurface,((width - timeRect.width)/2, 10))
    surface.blit(dateSurface,((width - dateRect.width)/2, 50))

    
    for row in range(0,len(data)):
        data[row].blitSummary (surface, scale, width, widgetHeight + (row * rowHeight * 2))
        


configData, iconData = loadConfig()
  
#device = get_device()
#font = makeFont("Dot Matrix Regular.ttf", 16)
#fontBold = makeFont("Dot Matrix Bold.ttf", 16)
#fontBoldLarge = makeFont("Dot Matrix Bold.ttf", 20)


inv = pygame.Surface(weatherIcons.get_rect().size, pygame.SRCALPHA)
inv.fill((255,255,0,255))
inv.blit(weatherIcons, (0,0), None, BLEND_RGB_SUB)
inv.set_colorkey((0,0,0))
iconRect = weatherIcons.get_rect()
iconSize = (int(iconRect.width / 7), int(iconRect.right / 7))

row = column = 0
canvas = pygame.Surface((widgetWidth * (forecastDays + 1), widgetHeight * (len(configData['beaches'])+1)))
canvasScreen = 0

if DEBUG:
    screen = pygame.display.set_mode((widgetWidth * (forecastDays + 1), widgetHeight * (len(configData['beaches'])+1)))
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


#Canvas
#    TIME                , FORECAST BEACH 1
#    KITEABLE BEACH 1/2  , FORECAST BEACH 2
#    KITEABlE BEACH 3/4  , FORECAST BEACH n


count = 0
while True:
    pygame.display.update() 
    canvas.fill(background)

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            exit()

    clock.tick(25)

    # This checks to see if the config should be refreshed or not.

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


    virtual = drawSignagePiGame(canvas, width=widgetWidth, height=widgetHeight, scale=widgetScale, data=beachData)
    #crop = (row * iconSize[0], column * iconSize[1], iconSize[0], iconSize[1])

    column += 1
    ##output = screen.blit(inv, (10, 10), crop)
    #column = column % 7
    #    row += 1
    ##if column == 0:
    #    row = row % 7

    #icons[count].showIcon (screen, 10, 10)

    timeNow = getEpochTime ()
#        virtual.refresh()

    
    screen.blit (canvas, (0,0))

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


        
pygame.quit()


#except KeyboardInterrupt:
#    pass
#except ValueError as err:
#    print(f"Error: {err}")
#except KeyError as err:
#    print(f"Error: Please ensure the {err} environment variable is set")
