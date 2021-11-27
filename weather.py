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

#list of all recipient carriers 
carriers = {
'att':    '@mms.att.net',
'tmobile':' @tmomail.net',
'verizon':  '@vtext.com',
'sprint':   '@page.nextel.com'}

def send(message, to_number, carrier):

    #try except for carrier
    to_number = to_number + '{}'.format(carriers[carrier.lower()])

    auth = ('weatheralerttoday@gmail.com', '***REMOVED***')

    # Establish a session with gmail's outgoing SMTP server
    # Need to have google allow less secure apps to make this work
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(auth[0], auth[1])

    #Send text message through SMS gateway of destination number
    server.sendmail(auth[0], to_number, message)

def get_long_lat(address_string):
    """Convert an address string to latitude and longitude coordinates""" 
    geolocator = Nominatim(user_agent = 'test')
    location = geolocator.geocode(address_string)
    assert location is not None, "Invalid address provided"
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude

def get_daily_weather(latitude, longitude, days_in_future = 0):
    """Return weather information at a specified latitude and longitude"""
    owm = pyowm.OWM('***REMOVED***')
    mgr = owm.weather_manager()
    one_call = mgr.one_call(latitude, longitude)
    fc = one_call.forecast_daily[days_in_future]
    rain = 1 if len(fc.rain) > 0 else 0  
    snow = 1 if len(fc.snow) > 0 else 0
    precip_prob = fc.precipitation_probability
    min_temp = fc.temperature('fahrenheit')['min']
    max_temp = fc.temperature('fahrenheit')['max']
    return rain, snow, precip_prob, min_temp, max_temp

def generate_message(rain, snow, precip_prob, min_temp, max_temp):
    """Generate summary weather report message"""

    min_max = "Expect a low of {}F and a high of {}F.".format(round(min_temp), round(max_temp))

    if snow == 1 and rain == 1:
        message = "It may snow and rain today. " + min_max

    elif snow == 1:
        message = "It may snow today. " + min_max

    elif rain == 1:
        message = "It may rain today. " + min_max

    else:
        message = "No rain or snow forecasted. " + min_max

    return message

if __name__ == '__main__':
    for user in users:
        latitude, longitude = get_long_lat(user['location'])
        rain, snow, precip_prob, min_temp, max_temp = get_daily_weather(latitude, longitude)
        message = generate_message(rain, snow, precip_prob, min_temp, max_temp)
        send(message, user['phone_number'], user['carrier'])
