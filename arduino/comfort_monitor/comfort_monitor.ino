/**
 * @author Jonathan Bonett
 * @create date 2021-07-07 19:00:00
 * @modify date 2021-07-07 19:00:00
 * @desc Thermal Comfort Model using Arduino Microcontroller and Tensorflow Lite, Web Interface connects to the device via BLE.
 */

#include "ArduinoBLE.h"
#include <Arduino_HTS221.h>

#include "EloquentTinyML.h"
#include "model.h"

#define PIN_ENABLE_SENSORS_3V3 (32u) // this is used just in case the sensors have issues, and we will power them down and up again

BLEService comfortService("19b10010-e8f2-537e-4f6c-d104768a1214"); // BLE Comfort Service
 
// BLE Comfort Characteristic - custom 128-bit UUID, read and notify by central
BLEStringCharacteristic comfortCharacteristic("19b10010-e8f2-537e-4f6c-d104768a1214", BLERead | BLENotify, 10);

#define NUMBER_OF_INPUTS 2
#define NUMBER_OF_OUTPUTS 100

#define TENSOR_ARENA_SIZE (NUMBER_OF_INPUTS + NUMBER_OF_OUTPUTS) * 1024

Eloquent::TinyML::TfLite<NUMBER_OF_INPUTS, NUMBER_OF_OUTPUTS, TENSOR_ARENA_SIZE> ml;

const int ledRed = 22; const int ledGreen = 23; const int ledBlue = 24;

int WINTER=0;
int SUMMER=1;
int CURRENT_MODEL_TYPE = SUMMER;
int resetSensorCount = 0;

bool load_model(int model_type) {
  if (model_type == WINTER) {
    Serial.println("Loading Winter Model");
    if (!ml.begin(comfort_model_winter)) {
      Serial.println("Cannot inialize model");
      Serial.println(ml.errorMessage());
    } else {
      Serial.println("Winter Model Loaded");
    }
    return true;
  } else {
    Serial.println("Loading Summer Model");
    if (!ml.begin(comfort_model_summer)) {
      Serial.println("Cannot inialize model");
      Serial.println(ml.errorMessage());
    } else {
      Serial.println("Summer Model Loaded");
    }
    return true;
  }
  return false;
}

void setup() {
    Serial.begin(9600);
    delay(2000);
    
    if (!HTS.begin()) {
      Serial.println("Failed to initialize humidity temperature sensor!");
      while (1);
    }
    
    if (!BLE.begin()) {
      Serial.println("starting BLE failed!");
      while (1);
    }
    // set LED pin to output mode
    pinMode(LEDR, OUTPUT);
    pinMode(LEDG, OUTPUT);
    pinMode(LEDB, OUTPUT);
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    
    digitalWrite(LEDR, HIGH);         // will turn the LED off
    digitalWrite(LEDG, LOW);        // will turn the LED on
    digitalWrite(LEDB, HIGH);        // will turn the LED off
    
    Serial.println("Initialising Model");
    load_model(CURRENT_MODEL_TYPE);
    

    // set advertised local name and service UUID:
    BLE.setLocalName("COMFORT");
    BLE.setAdvertisedService(comfortService);
   
    // add the characteristic to the service
    comfortService.addCharacteristic(comfortCharacteristic);
   
    // add service:
    BLE.addService(comfortService);
   
    // set the initial value for the characteristic:
    comfortCharacteristic.writeValue(String("0:" + String(CURRENT_MODEL_TYPE)));
   
    // start advertising
    BLE.advertise();
   
    Serial.println("BLE COMFORT Peripheral");
}

void loop() {
    // listen for BLE peripherals to connect:
    BLEDevice central = BLE.central();
   
    // if a central is connected:
    if (central) {
      Serial.print("Connected to central: ");
      // print the central's MAC address:
      Serial.println(central.address());
   
      // while the central is still connected to peripheral:
      while (central.connected()) {
        digitalWrite(LEDR, HIGH);         // will turn the LED off
        digitalWrite(LEDG, HIGH);       // will turn the LED off
        digitalWrite(LEDB, LOW);         // will turn the LED on
        
        Serial.println("Trying to predict the comfort level...");
        float temp = HTS.readTemperature();
        float humidity = HTS.readHumidity();
        if ( humidity == 0 ) {
          resetSensorCount = resetSensorCount + 1; 
          if (resetSensorCount > 5) {
            // most probably there's an issue with the sensor
            Serial.println("Problem with HTS sensor reading humidity");
            HTS.end();
            digitalWrite( PIN_ENABLE_SENSORS_3V3, LOW );
            delay(2000);
            digitalWrite( PIN_ENABLE_SENSORS_3V3, HIGH );
            if (!HTS.begin()) {
              Serial.println("Failed to initialize humidity temperature sensor!");
              while (1);
            }
            delay(3000);
            // tried to read the values again
            temp = HTS.readTemperature();
            humidity = HTS.readHumidity();
            resetSensorCount = 0;
          }
        }
        
        int comfort_percent = 0;
        if ((temp < 0) or (temp > 60)) {
          Serial.println("Temperature ranges are from 0 to 60 degrees Celcius");
        } else {
          float input[2] = { temp, humidity  };
          float output[100] = { 1 };
          ml.predict(input, output);
      
          Serial.print("temperatute=");
          Serial.print(temp);
          Serial.print(", humidity= ");
          Serial.print(humidity);
          Serial.print("\t predicted: ");
          
          float last_result = 0;
          for (int i=0; i<sizeof output/sizeof output[0]; i++)
          {
             float predicted_result = output[i];
             if (last_result < predicted_result) {
                last_result = predicted_result;
                comfort_percent = i; 
             }
          }
          Serial.print(comfort_percent);
          Serial.println("%");
        }
        
        comfortCharacteristic.writeValue(String(String(comfort_percent) + ":" + String(CURRENT_MODEL_TYPE)));
        comfortCharacteristic.writeValue(String(String(temp) + "|" + String(humidity)));
        delay(2000);
      }
   
      // when the central disconnects, print it out:
      Serial.print("Disconnected from central: ");
      Serial.println(central.address());
      digitalWrite(LEDR, LOW);            // will turn the LED on
      digitalWrite(LEDG, HIGH);         // will turn the LED off
      digitalWrite(LEDB, HIGH);         // will turn the LED off
    }
}
