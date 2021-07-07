# /**
#  * @author Jonathan Bonett
#  * @create date 2021-07-07 19:00:00
#  * @modify date 2021-07-07 19:00:00
#  * @desc Thermal Comfort Model using Arduino Microcontroller and Tensorflow Lite, Web Interface connects to the device via BLE.
#  */

import numpy as np
import tensorflow as tf

model_dir="models/comfort_summer"

def load_model():
    return tf.keras.models.load_model(model_dir)

def pred(y_pred, should_be):
    predication_calc = y_pred[0]
    np.set_printoptions(suppress=True)
    predication_calc = np.array(predication_calc)
    max_value = np.max(predication_calc)

    for i in range(len(predication_calc)):
        if (predication_calc[i] == max_value):
            print("{}%={} should be {}".format(i, predication_calc[i], should_be))

model = load_model()

y_pred = model.predict([[0,11.51]])
pred(y_pred, 0)

y_pred = model.predict([[25.91,11.51]])
pred(y_pred, 94)

y_pred = model.predict([[25.91,14.7]])
pred(y_pred, 94)

y_pred = model.predict([[23.95,41.61]])
pred(y_pred, 86)

y_pred = model.predict([[60,11.51]])
pred(y_pred, 0)

y_pred = model.predict([[31.59,34.53]])
pred(y_pred, 0)