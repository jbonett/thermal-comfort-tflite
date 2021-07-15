#include "DHTesp.h" // http://librarymanager/All#DHTesp
#include <LiquidCrystal_I2C.h>
DHTesp dht;
LiquidCrystal_I2C lcd(0x27, 16, 2);

#include "EloquentTinyML.h"
#include "model.h"

#define NUMBER_OF_INPUTS 2
#define NUMBER_OF_OUTPUTS 100

#define TENSOR_ARENA_SIZE (NUMBER_OF_INPUTS + NUMBER_OF_OUTPUTS) * 512 // reduced arena size due to ESP32 limitations

Eloquent::TinyML::TfLite<NUMBER_OF_INPUTS, NUMBER_OF_OUTPUTS, TENSOR_ARENA_SIZE> ml;

#define SCREEN_WIDTH 16

bool load_model() {
  // if you want to change to the winter model you change here
  Serial.println("Loading Summer Model");
  if (!ml.begin(comfort_model_summer)) {
    Serial.println("Cannot inialize model");
    Serial.println(ml.errorMessage());
  } else {
    Serial.println("Summer Model Loaded");
  }
  return true;
}

void printLcd(String text, int line) {
  int textPosition = (SCREEN_WIDTH - text.length())/2;
  lcd.setCursor(textPosition,line);
  lcd.print(text);
}

void setup()
{
  lcd.init();
  lcd.backlight();
  load_model();
}

void loop()
{
  TempAndHumidity tempHumidityData = dht.getTempAndHumidity();
  int comfort_percent = 0;
  if ((tempHumidityData.temperature < 0) or (tempHumidityData.temperature > 60)) {
    printLcd("0C to 60C only", 0);
  } else {
    float input[2] = { tempHumidityData.temperature, tempHumidityData.humidity  };
    float output[100] = { 1 };
    ml.predict(input, output);
    float last_result = 0;
    for (int i=0; i<sizeof output/sizeof output[0]; i++)
    {
      float predicted_result = output[i];
      if (last_result < predicted_result) {
        last_result = predicted_result;
        comfort_percent = i; 
      }
    }
    lcd.clear();
    printLcd(String(String(tempHumidityData.temperature) +  "C, " +String(tempHumidityData.humidity) + "%"), 0);
    printLcd(String(String(comfort_percent) +  "/100 Comfort"), 1);
  }
  delay(2000);
}
