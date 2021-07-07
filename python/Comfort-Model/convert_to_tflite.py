# /**
#  * @author Jonathan Bonett
#  * @create date 2021-07-07 19:00:00
#  * @modify date 2021-07-07 19:00:00
#  * @desc Thermal Comfort Model using Arduino Microcontroller and Tensorflow Lite, Web Interface connects to the device via BLE.
#  */

import tensorflow as tf

saved_model_dir = "models/comfort_winter"
model_output = "tflite/models/comfort_winter.tflite"

# Convert the model
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_dir) # path to the SavedModel directory
tflite_model = converter.convert()

# Save the model.
with open(model_output, 'wb') as f:
  f.write(tflite_model)