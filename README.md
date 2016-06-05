# GenerateWeather
This is a program for generating 24 hour testing data with interal as 30 minutes for weather model

To run the script, please use following code:</br>
  `python GenerateWeather.py --input input file path --output output file path`

Input file format should be as following:</br>
`location,timestamp,temperature,pressure,humidity`

In current version, 10 cities are available:
* Sydney
* Melbourne
* Canberra
* Brisbane
* Adelaide
* Gold Coast
* Uluru
* Perth
* Geraldton
* Bunbury 

##Assumption for initial value:
* initial temperature is in a range between -10℃ to 40℃ and tempreature at night should be lower than 20℃;
* initial pressure should be in a range between standard air pressure at 1000m height and pressure at sea level in -15℃;
* initial humidity should be in a range between 0 to 110;

##Trend in a day:
Since relation among temperature, pressure and humidity in meterology is too complicated, we simplized the relation into following regulations:
* Sun rise time is fixed as 06:00 and same for sun set time as 19:00. 14:30 is the time in a day which has a highest temperature.
* Temperature are linearly increase after sun rise and descrease after 14:30 but two times faster after sun set for sunny day.
* Using historical monthly minimum temperature and maximum temperature in sepecific location as the temperature range to get the slope of termperature changing during the day.
* for cloudy day, temperature still linearly increase and descrease, but the maximum temperature reduces 2 degree since radiation from solar is reduing, while minimum temperature increases 2 degree because of protection of cloud.
* for rain/snow, temperature will descrease a constant number in every 30 minutes
* pressure and humidity descrease constantly when temperature increases

##Climate type:
I introuded climate type as a factor in the model, for current version, 5 types are available:
*Humid Subtropical climate
*Mediterranean climate
*Hot Desert
*Dry Continental
*Oceanic

Each type would have a different effection on daily trend based on their key features.
