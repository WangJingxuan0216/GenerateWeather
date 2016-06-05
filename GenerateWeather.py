#!/usr/bin/python

from datetime import datetime, timedelta
import argparse
import random
from math import exp
import json

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def standard_pressure(altitude):
# calculate standard pressure by given the altitude of the location
# equation: P = P_o*e^(-Mgz/RT) z is altitude
	return exp(-0.0289644*9.8/(8.31432*273)*altitude)*1013.25

def reading_data(line):
	# converting original string data into dictionary
	# input: String
	# output: Dict
	column_names = ['location', 'timestamp', 'temperature', 'pressure', 'humidity']
	rows = line.strip().split(',')
	parsed_dict = {column_names[key]:value for key, value in enumerate(rows)} # parse data into a dictionary
	parsed_dict['temperature'] = float(parsed_dict['temperature'])
	parsed_dict['pressure'] = float(parsed_dict['pressure'])
	parsed_dict['humidity'] = int(parsed_dict['humidity'])
	maximum_T = 45
	minimum_T = -15
	minimum_P = standard_pressure(1000)

	## assuming if temperature drops 1 degree Celsius, pressure will increase 0.5hPa and vice versa, and maximum_P is the pressuer when temperature is equal to -10 degree Celsius
	maximum_P = standard_pressure(0) -(0 - 15)*0.5

	##initial temperature can't be higher than 40 or lower than -10
	if parsed_dict['temperature'] <minimum_T or parsed_dict['temperature'] > maximum_T:
		raise ValueError("initial temperature is odd, please check and rerun")
	
	##initial temperature at night should not be higher than 20
	if datetime.strptime(parsed_dict['timestamp'], DATETIME_FORMAT).hour not in range(6, 19):
		if parsed_dict['temperature'] > 20:
			raise ValueError("initial temperature is odd, please check and rerun")

	##initial pressure can't be higher than  or lower than -10
	if parsed_dict['pressure'] <minimum_P or parsed_dict['pressure'] > maximum_P:
		raise ValueError("initial pressure is odd, please check and rerun")
	
	##initial humidity should with in 0 - 110
	if parsed_dict['humidity'] not in range(0,110) :
		raise ValueError("initial humidity is odd, please check and rerun")
		if mapping_table[parsed_dict['location']]['climate'] == "hot_desert" and parsed_dict['humidity'] not in range(0,20):
			raise ValueError("initial humidity is odd, please check and rerun")
	return parsed_dict

def init_condition(data):
	# predict what is the weather condition(rain/snow/cloudy/sunny) by given tempeature, pressure and humidity
	# conditions:
	# 	for cloudy: temperature is above 20 degree Celsius(warm weather), pressure under standard pressure and humidity is above 50(not too dry)
	# 	for rain: temperature is greater than 0 degree Celsius and humidity is above 80
	# 	for snow: temperature is equal to or less than 0 degree Celsius and humidity is above 80
	# 	for sunny: all the other cases
	altitude = mapping_table[data['location']]['altitude'] ## getting altitude of the location
	temperature = data['temperature']
	pressure = data['pressure']
	humidity = data['humidity']

	data['condition'] = 'sunny'
	if humidity >= 80:
		if temperature > 0:
			data['condition'] = 'rain'
		else:
			data['condition'] = 'snow'
	if humidity >= 50 and temperature >= 20 and pressure < standard_pressure(altitude):
		data['condition'] = 'cloudy'
	return data

def trending(data, sunny_to_cloudy=0, cloudy_to_rain=0, cloudy_to_snow=0, rain_to_snow=0):
	
	#given current weather conditions and climate type, simulating the trend for next 30 minutes 
	#assumption: using monthly minimum temperature and maximum temperature as the temperature range, assuming sun rise time is fixed as 06:00 and same for sun set time as 19:00. 14:00 is the time in a day which has a highest temperature. 
	#	Implemented rules:
	#	Temperature are linearly increase and descrease but two times faster after sun set for sunny day.
	#	for cloudy day, temperature still linearly increase and descrease, but the maximum temperature reduces 2 degree, while minimum temperature increases 2 degree.
	#	for rain/snow, temperature will descrease a constant number in every 30 minutes
	#	relation between pressure and temperature: P_2 = P_1*T_2/T_1
	#	humidity will descrease when temperature increases
	
	cur_time = datetime.strptime(data['timestamp'], DATETIME_FORMAT)
	month = cur_time.month
	max_T = mapping_table[data['location']]['maximum_t'][month-1]
	min_T = mapping_table[data['location']]['minimum_t'][month-1]
	
	def estimated_temp(cur_hour, cur_temp, max_T, min_T):
		##calculating the increment/reduction by given current hour, maximum temperature and minimum temperature in the day
		
		T_increment_morning = (max_T - min_T)/((14-6)*2) ##getting increment of temperature in 30 minutes for time between 06:00 to 14:00
		T_increment_afternoon = (max_T - min_T)/((19-14)*2 + (24-19+6)*4) ##getting increment of temperature in 30 minutes for time between 14:00 to 19:00
		T_increment_evening = 2*T_increment_afternoon ##getting increment of temperature in 30 minutes for time between 19:00 to 06:00 in next day

		if cur_hour in range(6, 14):
			return cur_temp + T_increment_morning
		elif cur_hour in range(14, 19):
			return cur_temp - T_increment_afternoon
		else:
			return cur_temp - T_increment_evening

	def estimated_pressure(cur_pressure, cur_temp, new_temp):
		## assuming if temperature drops 1 degree Celsius, pressure will increase 0.5hPa and vice versa
		return cur_pressure + (cur_temp - new_temp)*0.5

	def estimated_humidity(cur_humidity, cur_temp, new_temp):
		if cur_humidity + int((new_temp -cur_temp)/0.5) > 0:
			return cur_humidity + int((new_temp -cur_temp)/0.5)
		else:
			return 0

	possibility = random.randint(1, 100)/100.0
	
	result = {}
	result['location'] = data['location']
	result['timestamp'] = (cur_time + timedelta(minutes = 30)).strftime(DATETIME_FORMAT)

	## weather is changing from sunny to cloudy
	if data['condition'] == "sunny":
		if possibility <= sunny_to_cloudy:
			result['condition'] = "cloudy"
			max_T = max_T - 2
			min_T = min_T + 2
			result['temperature'] = estimated_temp(cur_time.hour, data['temperature'], max_T, min_T)
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = estimated_humidity(data['humidity'], data['temperature'], result['temperature'])
		## weather remains as sunny:
		else:
			result['condition'] = data['condition']
			result['temperature'] = estimated_temp(cur_time.hour, data['temperature'], max_T, min_T)
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = estimated_humidity(data['humidity'], data['temperature'], result['temperature'])

	## weather is cloudy
	if data['condition'] == "cloudy":
		## weather is changing from cloudy to rain
		if possibility <= cloudy_to_rain and data['temperature'] >= 0 and data['humidity'] > 70:
			result['condition'] = "rain"
			result['temperature'] = data['temperature'] - 0.08
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = estimated_humidity(data['humidity'], data['temperature'], result['temperature'])

		## weather is changing from cloudy to snow
		elif possibility <= cloudy_to_snow and data['temperature'] < 0 and data['humidity'] > 70:
			result['condition'] = "snow"
			result['temperature'] = data['temperature'] - 0.05
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = estimated_humidity(data['humidity'], data['temperature'], result['temperature'])

		## weather remain as cloudy
		else:
			result['condition'] = data['condition']
			max_T = max_T - 2
			min_T = min_T + 2
			result['temperature'] = estimated_temp(cur_time.hour, data['temperature'], max_T, min_T)
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = estimated_humidity(data['humidity'], data['temperature'], result['temperature'])

	## weather is rain
	if data['condition'] == "rain":
		## weather is change from rain to snow
		if possibility <= rain_to_snow and data['temperature'] < 0.05:
			result['condition'] = "snow"
			result['temperature'] = data['temperature'] - 0.05
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = data['humidity'] ##humidity wouldn't go up when snowing/raining

		## weather remain as rain:
		else:
			result['condition'] = data['condition']
			result['temperature'] = data['temperature'] - 0.08
			result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
			result['humidity'] = data['humidity'] ##humidity wouldn't go up when snowing/raining

	## weather remain as snow:
	if data['condition'] == "snow":
		result['condition'] = data['condition']
		result['temperature'] = data['temperature'] - 0.05
		result['pressure'] = estimated_pressure(data['pressure'], data['temperature'], result['temperature'])
		result['humidity'] = estimated_humidity(data['humidity'], data['temperature'], result['temperature'])

	return result

def climate_factor(data):
	## estimate the weather change possibility by considering climate type of the location
	spring = [9, 10, 11]
	summer = [12, 1, 2]
	autumn = [3, 4, 5]
	winter = [6, 7, 8]
	
	

	location = data['location']
	timestamp = datetime.strptime(data['timestamp'], DATETIME_FORMAT)
	
	def humid_subtropical(month):
		##  humid subtropical climate is a zone of subtropical climate characterised by hot, usually humid summers and mild to cool winters.
		sunny_to_cloudy = cloudy_to_rain = cloudy_to_snow = rain_to_snow=0
		if month in spring or autumn:
			sunny_to_cloudy = 0.4
			cloudy_to_rain = 0.4
		if month in summer:
			sunny_to_cloudy = 0.6
			cloudy_to_rain = 0.6
		if month in winter:
			sunny_to_cloudy = 0.2
			cloudy_to_rain = 0.2
		return (sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow)

	def mediterranean(month):
		##  regions with this form of a mediterranean climate experience average monthly temperatures in excess of 22.0 degree Celsius during its warmest month and an average in the coldest month between 18 to -3 degree Celsius or, in some applications, between 18 to 0 degree Celsius. Regions with this form of the mediterranean climate typically experience hot, sometimes very hot and dry summers and mild, wet winters.
		sunny_to_cloudy = cloudy_to_rain = cloudy_to_snow = rain_to_snow=0
		if month in winter:
			sunny_to_cloudy = 0.6
			cloudy_to_rain = 0.6
			cloudy_to_snow = 0.5
			rain_to_snow = 0.4
		if month in spring or month in autumn:
			sunny_to_cloudy = 0.2
			cloudy_to_rain = 0.2
		if month in summer:
			sunny_to_cloudy = 0.05
			cloudy_to_rain = 0.05
		return (sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow)

	def hot_desert(month):
		## Hot desert climates feature hot, typically exceptionally hot, periods of the year. During colder periods of the year, night-time temperatures can drop to freezing or below.
		sunny_to_cloudy = cloudy_to_rain = cloudy_to_snow = rain_to_snow=0
		sunny_to_cloudy = 0.2
		cloudy_to_rain = 0.1
		return (sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow)

	def dry_continental(month):
		## annual rainfall spread fairly evenly over the seasons
		sunny_to_cloudy = cloudy_to_rain = cloudy_to_snow = rain_to_snow=0
		sunny_to_cloudy = 0.3
		cloudy_to_rain = 0.3
		if month in winter:
			cloudy_to_rain = 0.1
			cloudy_to_snow = 0.2
		return (sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow)

	def oceanic(month):
		## It typically lacks a dry season, as precipitation is more evenly dispersed throughout the year.
		sunny_to_cloudy = cloudy_to_rain = cloudy_to_snow = rain_to_snow=0
		sunny_to_cloudy = 0.5
		cloudy_to_rain = 0.5
		if month in winter:
			sunny_to_cloudy = 0.7
			cloudy_to_rain = 0.7
		return (sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow)

	if mapping_table[data['location']]['climate'] == "humid_subtropical":
		return humid_subtropical(timestamp.month)
	elif mapping_table[data['location']]['climate'] == "mediterranean":
		return mediterranean(timestamp.month)
	elif mapping_table[data['location']]['climate'] == "hot_desert":
		return hot_desert(timestamp.month)
	elif mapping_table[data['location']]['climate'] == "dry_continental":
		return dry_continental(timestamp.month)
	elif mapping_table[data['location']]['climate'] == "oceanic":
		return oceanic(timestamp.month)
	else:
		raise ValueError("Australia doesn't have this climate type, please varify your data")


def main(input_path, output_path):
	output_file = open(output_path,'w')
	with open('mapping_table.json', 'r') as mapping_file:
		mapping_data = mapping_file.read()
	global mapping_table
	mapping_table = json.loads(mapping_data)

	for line in open(input_path, 'r'):
		data = reading_data(line) ##reading and validating initial value
		data = init_condition(data)
		for i in range(24*2):
			(sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow) = climate_factor(data)
			new_data = trending(data, sunny_to_cloudy, cloudy_to_rain, cloudy_to_snow, rain_to_snow)
			iait_code = mapping_table[new_data['location']]['iait']
			coordinate = mapping_table[new_data['location']]['coordinate']
			output_file.write("|".join([iait_code, coordinate, new_data['timestamp'], new_data['condition'], str(new_data['temperature']), str(new_data['pressure']), str(new_data['humidity'])])+"\n")
			data = new_data

	output_file.close()



if __name__ == '__main__':
	## defining arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("--input", help="input file path")
	parser.add_argument("--output", help="output file path")
	args = vars(parser.parse_args())
	input_path = args['input']
	output_path = args['output']
	if input_path == None:
		raise ValueError("please give input file path after --input")
	if output_path == None:
		raise ValueError("please give output file path after --output")
	main(input_path, output_path)