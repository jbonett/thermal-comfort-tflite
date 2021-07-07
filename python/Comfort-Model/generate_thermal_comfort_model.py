# /**
#  * @author Jonathan Bonett
#  * @create date 2021-07-07 19:00:00
#  * @modify date 2021-07-07 19:00:00
#  * @desc Thermal Comfort Model using Arduino Microcontroller and Tensorflow Lite, Web Interface connects to the device via BLE.
#  */

import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow import keras

data_file="thermal_comfort_winter.csv"
model_dir="models/comfort_winter"
# summer test loss, test acc: [0.42216846346855164, 0.8630762696266174]
# winter test loss, test acc: [0.5069693326950073, 0.819187581539154]

def load_data():
    return pd.read_csv(data_file)

def save_model():
    df = load_data()
    max_value = 100 # as there can be up to 100%
    df['calculated_comfort'] = df['calculated_comfort'].astype('category')
    features = df.drop(columns=['pmv', 'ppd', 'how_it_feels', 'calculated_comfort'])

    target = df['calculated_comfort']

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=0, shuffle=True,
                                                        stratify=target)

    inputs = keras.Input(shape=X_train.shape[1])

    hidden_layer = keras.layers.Dense(10, activation="relu")(inputs)
    output_layer = keras.layers.Dense(max_value, activation="softmax")(hidden_layer)
    model = keras.Model(inputs=inputs, outputs=output_layer)
    model.compile(loss = 'sparse_categorical_crossentropy', optimizer = 'adam', metrics = ['accuracy'])

    history = model.fit(X_train, y_train, batch_size=300, epochs=20)

    print("Evaluate on test data")
    results = model.evaluate(X_test, y_test, batch_size=300)
    print("test loss, test acc:", results)

    model.save(model_dir)

def load_model():
    return tf.keras.models.load_model(model_dir)

if __name__ == '__main__':
    save_model()