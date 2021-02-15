from pysolar.solar import *
from pysolar.util import *

import pandas as pd 
import requests 
from datetime import datetime 
import time 
import pytz

def master():

    print('Forecasting Solar...')


    #initialize Solar farms

    class Solar:
        def __init__(self,lat,long,capacity):
            
            self.lat=lat
            self.long=long
            self.capacity=capacity
            self.efficiency=0.086 #average effiency in clear sky from the experimental data
            self.area=(capacity*10**6)/100 #based on 1KW solar panel= 10m^2

        
    Dunmanbridge= Solar(54.629270,-5.912440,5)
    Belfast_city_airport=Solar(54.624741,-5.854350,4.83)
    Ballygarvey=Solar(54.885239,-6.237280,8)
    Greater_Belfast=Solar(54.597286,-5.930120,200)

    solar_lst=[Dunmanbridge,Belfast_city_airport,Ballygarvey,Greater_Belfast]

    #initialize Belfast timezone
    Belfast = pytz.timezone('Europe/Belfast')

    #initialize total mwhr

    total_MWhr_S=0

     #The first for loop gets a response for weather data every 3 hours for 5 days in the future for a certain solar farm.
     #The second loop then converts the solar incidence to MWhr and outputs a total MWhr


    for solar in solar_lst:
        lat1=solar.lat
        lon1=solar.long
        args = {'lat': lat1, 'lon': lon1, 'appid': '6a849af5aa9413d2533ad0acd144b513'}
        response = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=args)
        
        time.sleep(1.1) #tells the programme to wait 1.1 seconds so we don't go over the api limit
        
        res=requests.get(response.url)
        data = res.json()
    
        count=data['cnt']
        date=data['list'][0]['dt_txt']

        for x in range(0, count):

            loc_dt=data['list'][x]['dt']
            dt=datetime.fromtimestamp(loc_dt)
        
            
            
            loc_dt2 = Belfast.localize(dt)
            
            alt = get_altitude(lat1, lon1,loc_dt2)
            rad =(radiation.get_radiation_direct(loc_dt2, alt))
            
            cloud=data['list'][x]['clouds']['all']/100

            power=rad*(solar.efficiency)*(solar.area)
           
            output=power*(1-(0.75*cloud**3))
            
            total_MWhr_S+=(output/1000000)*3
    
    avg_MWhr_S=total_MWhr_S/(count*3)  

    print("total_MWhr for solar = ", total_MWhr_S)
    print("avg_MWhr = ", avg_MWhr_S)
    

    print('Forecasting Wind... ')

    #read in the wind turbine data and assign variables
    wind = pd.read_excel('wind_cluster.xlsx') 
    lat = wind['latd'].values
    lon = wind['longd'].values
    capacity = wind['tot_capacity[MW]']  
    
    #initialize total mwhr
    total_MWhr_W=0 

    #The first for loop gets a response for weather data every 3 hours for 5 days in the future for a certain wind turbine.
    #The second loop then converts the wind speed to MWhr and outputs a total MWhr

    # Assume a cut in speed of 4 m/s and linear to 12 m/s with a cut off at 25 m/s
    # Also assume wind at 80m is 40% higher than that at 10m which the api predicts 

    for farm in range (0, len(lat)): 
        lat1=lat[farm]
        lon1=lon[farm]
        args = {'lat': lat1, 'lon': lon1, 'appid': '6a849af5aa9413d2533ad0acd144b513'}
        response = requests.get('http://api.openweathermap.org/data/2.5/forecast', params=args)
    
        time.sleep(1.1) #tells the programme to wait 1.1 seconds so we don't go over the api limit
    
        res=requests.get(response.url)
        data = res.json()
    
        count=data['cnt']
        
        max_capacity=capacity[farm]

        for x in range(0, count):
            wind_speed=data['list'][x]['wind']['speed']
    
            wind_speed=wind_speed*1.4
    
            if wind_speed < 4 or wind_speed > 25:
                y = 0
            if wind_speed >= 4 and wind_speed <= 12:
                y = (1/8)*wind_speed-0.5
            if wind_speed > 12 and wind_speed <= 35:
                y = 1
            output=y*max_capacity*3 #each time step is 3 hours so this is the MW.hr produced
            total_MWhr_W+=output

    avg_MWhr_W=total_MWhr_W/(count*3)

    print("total MWhr for wind = ", total_MWhr_W)
    print("avg MWhr = ", avg_MWhr_W)
   
    total_NI=round(total_MWhr_W,1)
    total_NI_avg=round(total_NI/count,1)

    n_t=datetime.fromtimestamp(data['list'][0]['dt'])
    f_t=datetime.fromtimestamp(data['list'][count-1]['dt'])


    print(f'total forecast = {total_NI} and average MW/hr = {total_NI_avg}')
    print(f'from {n_t} to {f_t}')
    


master()
    
    
    
    
        
        
        
        
        

        


    









