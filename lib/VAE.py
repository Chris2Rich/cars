import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, backend as K
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import numpy as np
import ast
import traceback
import json

latent_dim = 8

@tf.keras.utils.register_keras_serializable(package="Custom")
class VAELossLayer(layers.Layer):
    def call(self, inputs):
        x, x_decoded, z_mean, z_log_var = inputs

        # reconstruction loss
        recon = tf.reduce_mean(tf.square(x - x_decoded))
        recon_loss = K.mean(recon)

        # KL divergence
        kl = -0.5 * K.sum(1 + z_log_var - K.square(z_mean) - K.exp(z_log_var), axis=1)
        beta = 2
        kl_loss = beta * K.mean(kl)

        self.add_loss(recon_loss + kl_loss)
        return x_decoded

@tf.keras.utils.register_keras_serializable(package="Custom")
class Sampling(layers.Layer):
    def call(self, inputs):
        z_mean, z_log_var = inputs
        batch = K.shape(z_mean)[0]
        dim = K.int_shape(z_mean)[1]
        epsilon = tf.random.normal(shape=(batch, dim))
        return z_mean + tf.exp(0.5 * z_log_var) * epsilon

    def compute_output_shape(self, input_shape):
        return input_shape[0]

def encoder_architecture(inputs):
    x = layers.Dense(40)(inputs)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(80)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(120)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(120)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    z_mean = layers.Dense(latent_dim, name="z_mean")(x)
    z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)
    z = Sampling()([z_mean, z_log_var])

    encoder = keras.Model(inputs, [z_mean, z_log_var, z], name="encoder")
    return encoder, z_mean, z_log_var

def decoder_architecture():
    latent_inputs = keras.Input(shape=(latent_dim,))
    x = layers.Dense(40)(latent_inputs)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(40)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(80)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("gelu")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(40)(x)
    x = layers.Activation("softsign")(x)
    
    outputs = x

    decoder = keras.Model(latent_inputs, outputs, name="decoder")
    return decoder

def train_model():
    tf.config.list_physical_devices("GPU")

    raw_data = np.zeros((0))
    with open("data/training_data.txt") as file:
        raw_data = np.array(ast.literal_eval(file.readline())) 
    train_data, val_data = train_test_split(raw_data, test_size=0.2)

    inputs = keras.Input(shape=(40,))
    encoder, z_mean, z_log_var = encoder_architecture(inputs)
    decoder = decoder_architecture()

    # VAE Model
    decoded = decoder(encoder(inputs)[2])
    outputs = VAELossLayer()([inputs, decoded, z_mean, z_log_var])

    vae = keras.Model(inputs, outputs, name="vae")
    vae.compile(optimizer=keras.optimizers.Adam(learning_rate=0.01))

    vae.fit(train_data, epochs=50, batch_size=64, shuffle=True, validation_data=(val_data, val_data))

    encoder.save_weights("models/encoder.weights.h5", overwrite=True)
    decoder.save_weights("models/decoder.weights.h5", overwrite=True)
    vae.save_weights("models/vae.weights.h5", overwrite=True)

    vae.summary()

def load_encoder():
    # Encoder
    encoder, _, _ = encoder_architecture(keras.Input(shape=(40,)))
    encoder.load_weights("models/encoder.weights.h5")
    return encoder

def load_decoder():
    # Decoder
    decoder = decoder_architecture()
    decoder.load_weights("models/decoder.weights.h5")
    return decoder

def load_vae():
    inputs = keras.Input(shape=(40,))
    encoder, z_mean, z_log_var = encoder_architecture(inputs)
    decoder = decoder_architecture()

    # VAE Model
    decoded = decoder(encoder(inputs)[2])
    outputs = VAELossLayer()([inputs, decoded, z_mean, z_log_var])

    vae = keras.Model(inputs, outputs, name="vae")
    vae.load_weights("models/vae.weights.h5")
    return vae

def visualize_latent_space(encoder, data, labels, fig, method="tsne"):
    z_mean, _, _ = encoder.predict(data, batch_size=64)
    labels = labels[:len(data)]

    reducer = PCA(n_components=3)
    z_3d_pca = reducer.fit_transform(z_mean)

    reducer = TSNE(n_components=3, init='pca', random_state=42, perplexity=30)
    z_3d_tsne = reducer.fit_transform(z_mean)

    ax = fig.add_subplot(221, projection="3d")
    ax.scatter(z_3d_pca[:, 0], z_3d_pca[:, 1], z_3d_pca[:, 2], s=5, alpha=0.6)
    for i, label in enumerate(labels):
        if i % 25 == 0:
            ax.text(z_3d_pca[i, 0], z_3d_pca[i, 1], z_3d_pca[i, 2], str(label), fontsize=6, alpha=0.7)
    ax.set_title(f"Latent Space Visualization (PCA)")
    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2")
    ax.set_zlabel("Component 3")

    ax = fig.add_subplot(222, projection="3d")
    ax.scatter(z_3d_tsne[:, 0], z_3d_tsne[:, 1], z_3d_tsne[:, 2], s=5, alpha=0.6)
    for i, label in enumerate(labels):
        if i % 25 == 0:
            ax.text(z_3d_tsne[i, 0], z_3d_tsne[i, 1], z_3d_tsne[i, 2], str(label), fontsize=6, alpha=0.7)
    ax.set_title(f"Latent Space Visualization (TSNE)")
    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2")
    ax.set_zlabel("Component 3")

def analyze_latent_dimensions(encoder, data, fig):
    z_mean, _, _ = encoder.predict(data, batch_size=64)
    
    pca = PCA(n_components=z_mean.shape[1])
    pca.fit(z_mean)
    
    explained_variance = pca.explained_variance_ratio_
    
    ax = fig.add_subplot(223)
    ax.bar(range(1, len(explained_variance) + 1), explained_variance)
    ax.plot(range(1, len(explained_variance) + 1), np.cumsum(explained_variance), 'r-o')
    ax.set_title('Explained Variance by Principal Component')
    ax.set_xlabel('Principal Component')
    ax.set_ylabel('Explained Variance Ratio')
    
    ax2 = plt.gca().twinx()
    ax2.set_ylabel('Cumulative Explained Variance')
    ax2.set_ylim([0, 1.05])
    
    for i, var in enumerate(explained_variance):
        print(f"Dimension {i+1}: {var:.4f} ({var*100:.2f}% variance)")
    
    cumulative = np.cumsum(explained_variance)
    for i, cum_var in enumerate(cumulative):
        print(f"Dimensions 1-{i+1}: {cum_var:.4f} ({cum_var*100:.2f}% cumulative variance)")
        
    return explained_variance, cumulative

def load_model():
    return load_vae(), load_encoder(), load_decoder()

def get_trims():
    res = []
    for i in ["data/car_models/Mercedes-Benz.json"]: #glob.glob("data/car_models/**.json", recursive=True):
        with open(i, "r") as file:
            for brand, models in json.load(file).items():
                for model in models:
                    for model_name, versions in model.items():
                        for version in versions:
                            res.append(" ".join([model_name, version]))
    return res

try:
    train_model()

    vae, encoder, decoder = load_model()
    raw_data = np.array(ast.literal_eval(open("data/training_data.txt").readline()))
    
    fig = plt.figure(figsize=(6,6))

    visualize_latent_space(encoder, raw_data, get_trims(), fig)
    analyze_latent_dimensions(encoder, raw_data, fig)

    plt.tight_layout()
    plt.show()
except Exception:
    print(traceback.format_exc())
    while True:
        pass