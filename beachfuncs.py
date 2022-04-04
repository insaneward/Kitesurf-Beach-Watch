import time
import pygame

def getEpochTime ():
    epoch = int(time.time())
    return epoch;

def convertEpochTime (epoch):
    timestruct = time.localtime(epoch)
    return timestruct

def epochToStr (epoch):
    epochStr = time.asctime(time.gmtime(epoch))
    return epochStr

def epochToTS (epoch):
    return time.gmtime(epoch)

def getCurrentTimeZone():
    timestruct = time.localtime()
    return timestruct.tm_zone, timestruct.tm_gmtoff


def getTimeStruct ():
    return time.localtime()

def dateFromTS (timeInfo):
    return f'{timeInfo.tm_mday:02d}/{timeInfo.tm_mon:02d}/{timeInfo.tm_year}'

def deltaToString (delta):
    days,remain = divmod(delta, 86400)
    hours, remain = divmod(remain,3600)

    if days:
        timeStr = f'in {days} days'
    elif hours:
        timeStr = f'in {hours} hours'
    else:
        timeStr = 'now'

    return timeStr
         
def windDirectionFromDegrees(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    i = int((degrees + 11.25)/22.5)
    return directions[i % 16]


#Globals

DEMODATA = False
DEBUG    = True

forecastDays = 2
widgetScale = 2
widgetWidth = 256 * widgetScale
widgetHeight = 64 * widgetScale

rowHeight = (widgetHeight / 4)
columnWidth = (widgetWidth / 8)

pygame.init()
background = ((0,0,0))
fontName = "fonts/Hack-Regular.ttf"
#fontName = "fonts/Dot Matrix Bold.ttf"
font            = pygame.font.Font(fontName, 12 * widgetScale)
fontSmall       = pygame.font.Font(fontName, 8 * widgetScale)
fontSmaller     = pygame.font.Font(fontName, 6 * widgetScale)
fontTime        = pygame.font.Font(fontName, 16 * widgetScale)
fontDate        = pygame.font.Font(fontName, 10 * widgetScale)
fontWeather     = pygame.font.Font("fonts/MAweather-BB04.ttf", 20 * widgetScale)
arrowImg        = pygame.image.load('images/arrow.png')
arrowImg        = pygame.transform.scale(arrowImg, (8*widgetScale,8*widgetScale))
weatherIcons    = pygame.image.load('images/weather_icons.png')


timezone, timeoffset = getCurrentTimeZone()

beachData       = []
kiteData        = []
icons           = []
dayText         = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']