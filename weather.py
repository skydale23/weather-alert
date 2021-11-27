import smtplib
import schedule
import time
import pytz
import pyowm
import pandas as pd
import datetime
import json
import pickle
from geopy.geocoders import Nominatim

#Get user data (stored in json file)
with open('weather_users.txt', 'r') as f:
    users = json.load(f)
f.close()

#Get email password
with open('weather_pass.txt', 'r') as f:
    password = f.readline()
f.close()

#Set up other variables
start_time = datetime.time(7)
end_time = datetime.time(21)
execute_time = '7:00'

#list of all recipient carriers 
carriers = {
'att':    '@mms.att.net',
'tmobile':' @tmomail.net',
'verizon':  '@vtext.com',
'sprint':   '@page.nextel.com'
}

def send(message, to_number, carrier):

    #try except for carrier
    to_number = to_number + '{}'.format(carriers[carrier.lower()])

    auth = ('weatheralerttoday@gmail.com', 'Itsyaboy')

    # Establish a session with gmail's outgoing SMTP server
    # Need to have google allow less secure apps to make this work
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    #Send text message through SMS gateway of destination number
    server.sendmail(auth[0], to_number, message)

#function to change timezone
def convert_time_zone(start, convert_to):

    gmt = pytz.timezone('GMT')
    new_time_zone = pytz.timezone(convert_to)
    end_time = start.astimezone(new_time_zone)

    return end_time

def get_long_lat(address_string):
    
    geolocator = Nominatim(user_agent = 'test')

    try:
        location = geolocator.geocode(address_string)
    except AttributeError:
        print("")
    else:
        latitude = location.latitude
        longitude = location.longitude

    return latitude, longitude


def generate_message(location):

    owm = pyowm.OWM('08ce08de126e25469062d11550ee8e4c')
    fc = owm.three_hours_forecast(location)
    f = fc.get_forecast()

    df_columns = ['date_time', 'conditions', 'temp']
    data = []

    #Get data for each three hour period
    for weather in f:
        ref_time = weather.get_reference_time('date')
        date_time = convert_time_zone(ref_time, 'US/Eastern')
        conditions = weather.get_status()
        temp =  weather.get_temperature('fahrenheit')['temp_min']
        row = [date_time, conditions, temp]
        data.append(dict(zip(df_columns, row)))

    #Convert to dataframe
    weather_hours = pd.DataFrame(data)
    weather_hours['date'] = weather_hours['date_time'].apply(lambda x: x.date())
    weather_hours['time'] = weather_hours['date_time'].apply(lambda x: x.time())
    weather_hours['rain'] = weather_hours['conditions'].apply(lambda x: 1 if x == 'Rain' else 0)
    weather_hours['snow'] = weather_hours['conditions'].apply(lambda x: 1 if x == 'Snow' else 0)

    #Filter to only hours we care about
    weather_hours = weather_hours[(weather_hours['time'] >= start_time) & (weather_hours['time'] <= end_time)]

    #Convert to full-day view
    agg_cols = {"temp":["max", "min"], "snow": "max", "rain": "max"}
    weather_days = weather_hours.groupby('date').agg(agg_cols).reset_index()
    weather_days.columns = ['date', 'temp_max', 'temp_min', 'will_snow', 'will_rain']

    #Add the day's weather to historical database
    latest_weather = weather_days.iloc[0:1,:]
    weather_history = pd.read_pickle('weather_history.pkl')
    weather_history_new = weather_history.append(latest_weather, ignore_index=True)
    weather_history_new.to_pickle('weather_history.pkl')

    #Get variables for message
    max_today = weather_days.iloc[0:1,:].temp_max.item()
    min_today = weather_days.iloc[0:1,:].temp_min.item()
    snow_today = weather_days.iloc[0:1,:].will_snow.item()
    rain_today = weather_days.iloc[0:1,:].will_rain.item()

    #Generate message
    min_max = "Expect a low of {}F and a high of {}F.".format(round(min_today), round(max_today))

    if snow_today == 1 and rain_today == 1:
        message = "It may snow and rain today. " + min_max

    if snow_today == 1:
        message = "It may snow today. " + min_max

    if rain_today == 1:
        message = "It may rain today. " + min_max

    else:
        message = "No rain or snow forecasted. " + min_max

    return message

for user in users:
    message = generate_message(user['location'])
    send(message, user['phone_number'], user['carrier'])


'''
def job():
    for user in users:
        message = generate_message(user['location'])
        send(message, user['phone_number'], user['carrier'])

schedule.every().day.at(execute_time).do(job)


while True:
    schedule.run_pending()
    time.sleep(60) # wait one minute
'''