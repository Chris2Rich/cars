import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np

latent_dim = 6  # Size of latent space

# Encoder
inputs = keras.Input(shape=(54,))
x = layers.Dense(108, activation="tanh")(inputs)
x = layers.Dropout(0.12)(x)
x = layers.Dense(216, activation="tanh")(x)
x = layers.Dropout(0.25)(x)
x = layers.Dense(60, activation="relu")(x)
x = layers.Dense(30, activation="relu")(x)

z_mean = layers.Dense(latent_dim, name="z_mean")(x)
z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)

# Reparameterization trick
def sampling(args):
    z_mean, z_log_var = args
    batch = tf.shape(z_mean)[0]
    dim = tf.shape(z_mean)[1]
    epsilon = tf.keras.backend.random_normal(shape=(batch, dim))
    return z_mean + tf.exp(0.5 * z_log_var) * epsilon

z = layers.Lambda(sampling, output_shape=(latent_dim,))([z_mean, z_log_var])

encoder = keras.Model(inputs, [z_mean, z_log_var, z], name="encoder")

# Decoder
latent_inputs = keras.Input(shape=(latent_dim,))
x = layers.Dense(30, activation="relu")(latent_inputs)
x = layers.Dense(60, activation="relu")(x)
x = layers.Dense(216, activation="tanh")(x)
x = layers.Dropout(0.25)(x)
x = layers.Dense(108, activation="tanh")(x)
x = layers.Dropout(0.12)(x)
outputs = layers.Dense(54, activation="sigmoid")(x)

decoder = keras.Model(latent_inputs, outputs, name="decoder")

# VAE Model
outputs = decoder(encoder(inputs)[2])
vae = keras.Model(inputs, outputs, name="vae")

# Loss function
reconstruction_loss = tf.reduce_mean(
    tf.keras.losses.mse(inputs, outputs)
)
kl_loss = -0.5 * tf.reduce_mean(1 + z_log_var - tf.square(z_mean) - tf.exp(z_log_var))
vae_loss = reconstruction_loss + kl_loss

vae.add_loss(vae_loss)
vae.compile(optimizer="adam")

# Summary
vae.summary()