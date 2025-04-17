import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, backend as K
from sklearn.model_selection import train_test_split
import numpy as np
import ast

def train_model():
    try:
        tf.config.list_physical_devices("GPU")

        raw_data = np.zeros((0))
        with open("data/training_data.txt") as file:
            raw_data = np.array(ast.literal_eval(file.readline())) 
        train_data, val_data = train_test_split(raw_data, test_size=0.125)


        latent_dim = 12  # Size of latent space

        # Encoder
        inputs = keras.Input(shape=(40,))
        x = layers.Dense(80, activation="tanh")(inputs)
        x = layers.GaussianDropout(0.2)(x)
        x = layers.Dense(80, activation="tanh")(x)
        x = layers.GaussianDropout(0.2)(x)
        x = layers.Dense(160, activation="tanh")(x)
        x = layers.GaussianDropout(0.2)(x)
        x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
        x = layers.Dense(160, activation="tanh")(x)
        x = layers.GaussianDropout(0.2)(x)

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
        x = layers.Dense(20, activation="gelu")(latent_inputs)
        x = layers.GaussianDropout(0.1)(x)
        x = layers.Dense(40, activation="gelu")(x)
        x = layers.GaussianDropout(0.2)(x)
        x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
        x = layers.Dense(80, activation="gelu")(x)
        x = layers.GaussianDropout(0.3)(x)
        x = layers.Dense(160, activation="tanh")(x)
        outputs = layers.Dense(40, activation="sigmoid")(x)

        decoder = keras.Model(latent_inputs, outputs, name="decoder")

        class VAELossLayer(layers.Layer):
            def call(self, inputs):
                x, x_decoded, z_mean, z_log_var = inputs

                # reconstruction loss
                recon = tf.reduce_mean(tf.square(x - x_decoded))
                recon_loss = K.mean(recon)

                # KL divergence
                kl = -0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=1)
                beta = 0.7
                kl_loss = beta * K.mean(kl)

                self.add_loss(recon_loss + kl_loss)
                return x_decoded

            def get_config(self):
                config = super(VAELossLayer, self).get_config()
                return config

        # VAE Model
        decoded = decoder(encoder(inputs)[2])
        outputs = VAELossLayer()([inputs, decoded, z_mean, z_log_var])

        vae = keras.Model(inputs, outputs, name="vae")
        vae.compile(optimizer=keras.optimizers.Adam(learning_rate=0.005))

        vae.fit(train_data, epochs=250, batch_size=64, shuffle=True, validation_data=(val_data, val_data))
        vae.save("models/VAE.keras")
        encoder.save("models/encoder.keras")
        decoder.save("models/decoder.keras")
        vae.summary()
    except Exception as e:
        print(e)

def load_model():
    return keras.models.load_model("models/VAE.keras"), keras.models.load_model("models/encoder.keras"), keras.models.load_model("models/decoder.keras")

train_model()
print("TRAINED and SAVED")
while True:
    pass