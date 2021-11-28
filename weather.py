import smtplib
import pyowm
import json
import yaml
from geopy.geocoders import Nominatim


def read_yaml(file):
    with open(file, "r") as f:
        try:
            yaml_file = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)
    return yaml_file 

def read_json(file):
    with open('weather_users.json', 'r') as f:
        try:
            users = json.load(f)
        except Exception as e:
            print("Couldn't read json file")
    return users 

def send_email_to_cell_phone(message, to_number, carrier_domain, from_email, from_password):
    """Send email to a user specified cell phone number and carrier"""
    #number to send to 
    to_number = to_number + '{}'.format(carrier_domain)
    # Establish a session with gmail's outgoing SMTP server
    # Need to have google allow less secure apps to make this work
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, from_password)
    #Send text message through SMS gateway of destination number
    server.sendmail(from_email, to_number, message)

def get_long_lat(address_string):
    """Convert an address string to latitude and longitude coordinates""" 
    geolocator = Nominatim(user_agent = 'test')
    location = geolocator.geocode(address_string)
    assert location is not None, "Invalid address provided"
    latitude = location.latitude
    longitude = location.longitude
    return latitude, longitude

def get_daily_weather(latitude, longitude, api_key, days_in_future = 0):
    """Return weather information at a specified latitude and longitude"""
    owm = pyowm.OWM(api_key)
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
    
    creds = read_yaml("credentials.yml")
    config = read_yaml("config.yml")
    users = read_json("weather_users.json")

    # get credentials required to execute script
    gmail_username = creds['gmail']['username']
    gmail_password = creds['gmail']['password']
    pyowm_api_key = creds['pyowm']['api_key']

    for user in users:
        # get user-specific configs
        location = user['location']
        phone = user['phone_number']
        carrier = user['carrier'].lower()
        carrier_email_domain = config['carrier_email_domain'][carrier]
        
        # generate and send message
        latitude, longitude = get_long_lat(location)
        rain, snow, precip_prob, min_temp, max_temp = get_daily_weather(latitude, longitude, pyowm_api_key)
        message = generate_message(rain, snow, precip_prob, min_temp, max_temp)
        send_email_to_cell_phone(message, phone, carrier_email_domain,
            gmail_username, gmail_password)
