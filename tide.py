from bs4 import BeautifulSoup
import time
import requests
from beachfuncs import *

#Llanelli       https://www.worldtides.info/api/v3?extremes&date=2022-03-31&lat=51.6754617&lon=-4.177041&days=7&key=a954c406-8135-4b13-aef5-0efae7ac6cbd
#Pembrey      https://www.worldtides.info/api/v3?extremes&date=2022-03-31&lat=51.674573&lon=-4.315011&days=7&key=a954c406-8135-4b13-aef5-0efae7ac6cbd



class Tide:
    def __init__ (self,tide_station, tide_window):
        self.tides = []
        self.tide_station = tide_station
        self.tide_window = tide_window
        self.spring_date = None
        self.spring_diff = None
        self.neap_date = None
        self.neap_diff = None
        self.tides_url = "https://www.tide-forecast.com/locations/"+self.tide_station+"/tides/latest"

    def getTideForecast (self, name):

        filename = f'data/{name} - tides.html'

        if DEMODATA:
            with open(filename, 'r') as f:
                content = f.read()
                f.close()
            soup = BeautifulSoup(content, "html.parser")
                
        else:

            response = requests.get(self.tides_url)

            with open(filename, 'w') as f:
                f.write(str(response.content))
                f.close()

            soup = BeautifulSoup(response.content, "html.parser")

        header = soup.find('p', class_='tide-header-summary')
        x = header.get_text().find(' for')
        date = header.get_text()[34:x]

        header = soup.find ('span', class_='tide-table-header__subtitle')
        tzinfotext = header.get_text()
        today = soup.find('div', class_='tide-header-today__table-container')
        today_rows = today.find_all('tr', attrs={'itemtype': None})
   
        dayTides = []
        for x in range(0, len(today_rows)):
            tide_row = today_rows[x]
            tide_type = tide_row.find('td')
            tide_time = tide_type.find_next('b')
            tide_height = tide_time.find_next('td').find('b')
            tide_type = tide_type.get_text().strip()
            tide_time = tide_time.get_text().strip()
            if tide_time[0:2] == '00':
                tide_time = '12' + tide_time[2:]
            datetime_object = time.strptime(str(date)+' '+tide_time,'%A %d %B %Y %I:%M %p')

            tide_height = tide_height.get_text().strip()
            tide_height = float(tide_height[0:tide_height.find(' ')])
            utc = int(time.mktime (datetime_object))
            dayTides.append([utc,datetime_object, tide_type,tide_height])
        self.tides.append([datetime_object, dayTides.copy()])
        dayTides.clear()

        output = soup.find_all('div', class_='tide-day')
        for day in output:
            # Extract day
            date = day.find('h4').get_text()
            date = date[date.find(': ')+2:len(date)].strip()

            datetime_object = time.strptime(str(date),'%A %d %B %Y')
            today_rows = day.find_all('tr', attrs={'itemtype': None})

            for x in range(0,len(today_rows)-1):
                tide_row = today_rows[x]
                tide_type = tide_row.find('td')
                tide_time = tide_type.find_next('b')
                tide_height = tide_time.find_next('td').find('b')
                tide_type = tide_type.get_text().strip()
                tide_time = tide_time.get_text().strip()
                if tide_time[0:2] == '00':
                    tide_time = '12' + tide_time[2:]
                datetime_object = time.strptime(str(date)+' '+tide_time,'%A %d %B %Y %I:%M %p')

                tide_height = tide_height.get_text().strip()
                tide_height = float(tide_height[0:tide_height.find(' ')])
                utc = int(time.mktime (datetime_object))
                dayTides.append([utc,datetime_object, tide_type,tide_height])

            self.tides.append([datetime_object, dayTides.copy()])
            dayTides.clear()

    def printTides (self):
        for days in self.tides:
            print (f'{time.strftime("%d %b %y",days[1][0][1]):<} :', end="")
            for tides in days[1]:
                print (f' {time.strftime("%H:%M",tides[1]):5s}, {tides[3]:.2f}m, {tides[2]:<9}', end="")
            print ("")
