# Weather Alert

`weather_alert` is a project I built to send myself weather alerts from a gmail account to my cellphone 

### Why?

1. Sometimes I am blindsided by colder weather than expected or by precipitation. There are lots of apps and websites I could use actively to get weather reports, but this solution is more passive; I get a text every morning.
2. This was a good opportunity to learn more about packages like smtplib, pyowm, and geopy.

### How to use

If you want to leverage this code, follow the steps below:

1. Fork the project
2. Install the packages in requirements.txt file. 
3. Get an api_key from [open weather map](https://openweathermap.org/appid)
4. Create a credentials.yml file. You'll need to add an api key, and a gmail user name, and password. Follow the format in the credentials_template.yml file and replace with your specific credential values. Make sure the file is named "credentials.yml"
5. Set up a cronjob (or preferred scheduling solution) to run the script on a regular basis.
