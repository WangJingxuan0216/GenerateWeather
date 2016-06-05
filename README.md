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

Assumption in the algorithm:
1. initial temperature is in range between -10 ℃ to 40;
2. initial tempreature at night should be lower than 20
