# /**
#  * @author Jonathan Bonett
#  * @create date 2021-07-07 19:00:00
#  * @modify date 2021-07-07 19:00:00
#  * @desc Thermal Comfort Model using Arduino Microcontroller and Tensorflow Lite, Web Interface connects to the device via BLE.
#  */

import csv

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from pythermalcomfort.models import pmv_ppd
from pythermalcomfort.utilities import v_relative

fileToSave = "thermal_comfort_winter.csv"
airSpeed = 0.1  # metres per second

# **** Activity MET Units ****
# Reclining, Sleeping	0.8
# Seated relaxed	1
# Seated office work    1.1
# Standing at rest	1.2
# Sedentary activity (office, dwelling,	1.2
# school, laboratory)
# Car driving	1.4
# Graphic profession - Book Binder	1.5
# Standing, light activity (shopping, laboratory, light industry)	1.6
# Teacher	1.6
# Domestic work -shaving, washing and dressing	1.7
# Walking on the level, 2 km/h	1.9
# Standing, medium activity (shop assistant,	2
# domestic work)
# Building industry - Brick laying (Block of 15.3 kg)	2.2
# Washing dishes standing	2.5
# Domestic work - raking leaves on the lawn	2.9
# Domestic work - washing by hand and ironing (120-220 W)	2.9
# Iron and steel - ramming the mold with a	3
# pneumatic hammer
# Building industry - forming the mold	3.1
# Walking on the level, 5 km/h	3.4
# Forestry - cutting across the grain with a	3.5
# one-man power saw
# Volleyball, Bicycling (15 km/h)	4
# Calisthenics	4.5
# Building industry - loading a wheelbarrow with stones and mortar	4.7
# Golf, Softball	5
# Gymnastics	5.5
# Aerobic Dancing, Swimming	6
# Sports - Ice skating, 18 km/h, Bicycling (20 km/h)	6.2
# Agriculture - digging with a spade (24 lifts/min.)	6.5
# Skiing on level (good snow, 9 km/h), Backpacking, Skating ice or roller, Basketball, Tennis	7
# Handball, Hockey, Racquetball, Cross County Skiing, Soccer	8
# Running 12 min/mile, Forestry - working with an axe (weight 2 kg. 33 blows/min.)	8.5
# Sports - Running in 15 km/h	9.5
metValue = 1.1  # seated office work

# **** Indoor clothes values ****
# 0.36 Walking shorts, short-sleeve shirt: 0.36 clo
# 0.5 Typical summer indoor clothing: 0.5 clo
# 0.54 Knee-length skirt, short-sleeve shirt, sandals, underwear: 0.54 clo
# 0.57 Trousers, short-sleeve shirt, socks, shoes, underwear: 0.57 clo
# 0.61 Trousers, long-sleeve shirt: 0.61 clo
# 0.67 Knee-length skirt, long-sleeve shirt, full slip: 0.67 clo
# 0.74 Sweat pants, long-sleeve sweatshirt: 0.74 clo
# 0.96 Jacket, Trousers, long-sleeve shirt: 0.96 clo
# 1 Typical winter indoor clothing: 1.0 clo
clothesValue = 1.0

# default configs
ashraeComfortableMax=100
# lowest temp will be 0 degrees celcius
rangeTempData = {'min': 0, 'max': 60} # °C The current official highest registered air temperature on Earth is 56.7 °C (134.1 °F), recorded on 10 July 1913 at Furnace Creek Ranch, in Death Valley in the United States.
rangeHumidityData = {'min': 0, 'max': 100}

# ASHRAE Standard 55-2020
ashraeRangeTempData = {'min': 19.5, 'max': 27.0}
ashraeRangeHumidityData = {'min': 19.8, 'max': 86.5}
step = 0.01
# calculate relative air speed
v_r = v_relative(v=airSpeed, met=metValue)

def f_range(start, end, step):
    a = range(int(start/0.01), int(end/0.01), int(step/0.01))
    var = []
    for item in a:
        var.append(round(item*0.01, 2)) # round to 2 dp
    return var


def convertPMV(pmv_value):
    result = 'neutral'

    if (pmv_value > 0.5):
        result = 'slightly_warm'

    if (pmv_value > 1.5):
        result = 'warm'

    if (pmv_value > 2.5):
        result = 'hot'

    if (pmv_value <= 0.5):
        result = 'neutral'

    if (pmv_value <= -0.5):
        result = 'slightly_cool'

    if (pmv_value <= -1.5):
        result = 'cool'

    if (pmv_value <= -2.5):
        result = 'cold'

    return result


def generateComfortRanges():
    generateTempRange = f_range(rangeTempData['min'], rangeTempData['max'] + step, step)
    generateHumidityRange = f_range(rangeHumidityData['min'], rangeHumidityData['max'] + step, step)

    resultArray = []
    current_count = 0
    for temperature in generateTempRange:
        for humidity in generateHumidityRange:
            results = pmv_ppd(tdb=temperature, tr=temperature, vr=v_r, rh=humidity, met=metValue, clo=clothesValue, wme=0,
                                  standard="ISO")
            pmv = results['pmv']
            ppd = results['ppd']
            calculatedComfort = (ashraeComfortableMax - ppd)
            if (calculatedComfort < 0):
                calculatedComfort = 0

            resultArray.append([temperature, humidity, pmv, ppd, convertPMV(pmv), round(calculatedComfort, 0)])

            if (current_count > 10000):
                print([temperature, humidity, pmv, ppd, convertPMV(pmv), round(calculatedComfort, 0)])
                current_count = 0

            current_count = current_count + 1

    return resultArray

if __name__ == '__main__':
    print("Starting...")
    results = generateComfortRanges()
    print("Going to save file...")
    current_count = 0
    with open(fileToSave, "w") as fh:
        writer = csv.writer(fh, delimiter=',')
        writer.writerow(['temperature', 'humidity', 'pmv', 'ppd', 'how_it_feels', 'calculated_comfort'])
        for item in results:
            writer.writerow([item[0], item[1], item[2], item[3], item[4], item[5]])
            if (current_count > 10000):
                print("Saving", [item[0], item[1], item[2], item[3], item[4], item[5]])
                current_count = 0

            current_count = current_count + 1

    print("Ready.")