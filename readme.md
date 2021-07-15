# ![alt text](/screenshots/global_warming.jpeg "Fight Global Warming") Welcome to Comfort Monitor ![alt text](/screenshots/global_warming.jpeg "Fight Global Warming") 

##### Help to Reduce Global Warming by controlling your Air Conditioning Energy Consumption in a Smarter Way!
![](/videos/demo.gif)

Running the model using an Arduino Nano 33 BLE Sense Chip and a Web application in a Chrome Browser
###### Imagine a buildings fitted with this Comfort Prediction Model where Air Conditioning Temperature can be adjusted in a smarter way by taking into consideration the comfort level.

![alt text](/screenshots/i2c.jpeg "i2c")
Running the model on an ESP32 connected to an i2c 16x2 display
## Introduction
The project has been created to predict the comfort level of an indoor area based on it's Temperature and Humidity. 

Conceptually humans understand that the comfort level is based on just temperature and rarely take humidity in consideration as most air conditioning units do not provide this information.

With the use of this project, you can program an Arduino Nano 33 BLE Sense device to detect what is the comfort level from 0-100, 100 being the most comfortable. This uses a predictable model based on the concept of Thermal Comfort.

The library pythermalcomfort from Python is used to create data sheet for summer/winter models, then using a TensorFlow model, we generate a compiled model to be used on our Arduino Device. This has an accuracy loss of around 2-3% comfort level units against the real generate data, but in our case is good enough to deduce the comfort level of the area.

I hope the project will be useful for both home and office environments, and in turn reduces the extra cost and energy used to cool/heat these areas through air conditioning.

## Installation
#### Arduino
To build the project you need to have Arduino ide setup, and your Arduino Nano 33 BLE Sense connected. Open the project inside the arduino folder, before starting you need to download the following libraries :
ArduinoBLE - Bluetooth Low Energy Library
Arduino_HTS221 - HTS221 Temperature and Humidity library
EloquentTinyML - This is a library which has preset and configured the Tensorflow Lite packages required for Arduino, more information can be found here https://github.com/eloquentarduino/EloquentTinyML

#### Python
I recommend pyCharm(jetbrains.com/pycharm/) to open this project, once pyCharm is installed you need to make sure you use Python 3 or greater to run the project

#### Web
The web folder contains the static html files which you'll, any good text editor can be used for these. You can open index.html in Chrome(or any other browser with BLE support) to get started.

## Running
#### Python
In the folder there are the following projects and script -
##### generate_thermal_comfort_data.py
  In this python program you need to change the fileToSave parameter to save the data generated to a csv file. Apart from the filename you can set the following : 
> - metValue - see the list of actions, by default 1.1 is seated office work, you can see the list in the script to check the other options 
> - clothesValue - this is the clothes type you are wearing usually 0.5 for summer and 1.0 for winter clothing  
##### generate_thermal_comfort_model.py
You run this script to generate the Tensorflow models for Summer and Winter, this will read the csv file generated from the generate_thermal_comfort_data.py script and use it to compile the model. The following are the parameters you can set :
> data_file="thermal_comfort_winter.csv" -> You set the input csv file that was generated from the previous script
> model_dir="models/comfort_winter" -> you set the output model directory (default models are already added to this repo)
##### test_comfort_model.py

After generating the Tensorflow Model you can use this script to test it, the following parameter can be changed to load the relevant model :
> model_dir="models/comfort_summer"

If you want to do a custom prediction you can add in the bottom area something like the following :

> y_pred = model.predict([[0,11.51]])
> pred(y_pred, 0)

Where the above will try to do a prediction with 0 degrees celcius and a humidity of 11.51, the Zero value here is the result expected pred(y_pred, 0), so you can test accordingly what you are getting as a prediction and what the actual output should be.

- convert_to_tflite.py
Once the TensorFlow model is generated, you can use this script to convert the model to TFLite
> saved_model_dir = "models/comfort_winter"
> model_output = "tflite/models/comfort_winter.tflite"
The above parameters can be set to indicate the location of the original TF model and the output folder to store the TensorFlow Lite file in.

- convert_model.sh
Finally this script(runs on linux/mac) will take the tflite file and convert it to .CC which this can be used in the Arduino IDE, you can see in the Arduino project how the model is stored inside the "model.h" file

#### Arduino Nano 33 BLE Sense
To install the project on your connected Arduino Nano 33 BLE Sense microcontroller, you need to make sure that the arduino device is connected, and select the appropriate port, then deploy to the device by clicking the Upload button from the tool bar. If you have any missing libraries you need to install them through library manager as explain in the installation section of this document.

>int CURRENT_MODEL_TYPE = SUMMER;
The above parameter can be set depending on what season it is, in this case SUMMER or WINTER

#### Arduino Esp32
Esp32 Version of the Code added in arduino/esp32/comfort_monitor, you would need an i2c 16x2 display and a DHT22 Temperature & Humidity monitor to build the system. Schematics for pins can be found based on the version of the hardware you have. But below you can find the pinout configuration for a widely used Esp32 chipset.

![alt text](/screenshots/esp32_dht22_i2c_schematics.png "Schematics")

#### Web
You can use different methods to run the files in a webserver, but to test it you just need to load the index.html file in a browser which supports BLE, Chrome would be one of the best options. When the webpage loads, you need to make sure that the BLE Sense Arduino device is powered and near-by. Then click Connect, and you should see a dialog which will show the device to pair with. Pair with the device (usually it's named Comfort/Arduino), and wait for the values to start updating.

The comfort level is based on the Season you have setup in Arduino before you uploaded the firmware. 100 means it's perfect, 0 means it not that comfortable.

Click the Connect Button as displayed below :
> ![alt text](/screenshots/web_0.png "Connecting")

Find the Arduino BLE device and click Pair :
> ![alt text](/screenshots/web_1.png "Pairing")

Below is the web application running :
> ![alt text](/screenshots/web_2.png "Connected")

#### Data around the project
Although there are various ways to measure comfortness, the data in this project is using a formula based on Predicted Mean Vote and Predicted Percentage of Dissatisfied. More information can be found here https://en.wikipedia.org/wiki/Thermal_comfort

#### Could this be done without using the TensorFlow Lite Machine Learning Model?
The following questions can be raised, and an answer is provided for each one.
> ###### Can we store the CSV files generated and we just read from them?
> The size of the data for just one season i.e. Summer or Winter is of around 2Gigabytes, therefore we cannot store this data on the small amount of memory in a microcontroller. 
> ###### Can we replicate the PMV & PPV formulas in an algorithm to be used in a Microcontroller?
> Yes, they can be replicated if you know all the mathematics and parameters involved. But it's much easier and faster to generate a TensorFlow Model by training it on pre-populated data than building the algorithm from scratch. The pythermalcomfort (https://pypi.org/project/pythermalcomfort/) is used to generate this data quickly and easily.
> ###### Can we read the data from the internet?
> Yes, but it defeats the scope for running everything locally on the microcontroller device. Also to read the large amounts of data or execute the algorithm code you will need a server running on the internet.