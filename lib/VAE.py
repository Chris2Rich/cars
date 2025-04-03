import keras
import numpy

Encoder = keras.Sequential()
Encoder.add(keras.layers.InputLayer((54), 32, float))
Encoder.add(keras.layers.Dense(108, activation="tanh"))
Encoder.add(keras.layers.Dropout(0.12))
Encoder.add(keras.layers.Dense(216, activation="tanh"))
Encoder.add(keras.layers.Dropout(0.25))
Encoder.add(keras.layers.Dense(54, activation="relu"))
Encoder.add(keras.layers.Dense(27, activation="relu"))