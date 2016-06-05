# GenerateWeather
This is a program for generating testing data for weather model

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

Assumption for initial value:
1. initial temperature is in a range between -10℃ to 40℃ and tempreature at night should be lower than 20℃;
2. initial pressure should be in a range between standard air pressure at 1000m height and pressure at sea level in -15℃;
3. initial humidity should be in a range between 0 to 110;

Assumption in algorithm:
Since relation among temperature, pressure and humidity in meterology is too complicated, we simplized the relation into following regulations:
1. 
