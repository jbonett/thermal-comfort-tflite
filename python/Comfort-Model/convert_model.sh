rm ./tflite/models/comfort_summer.cc
rm ./tflite/models/comfort_winter.cc
xxd -i ./tflite/models/comfort_summer.tflite > ./tflite/models/comfort_summer.cc
xxd -i ./tflite/models/comfort_winter.tflite > ./tflite/models/comfort_winter.cc
