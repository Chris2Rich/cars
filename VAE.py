import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, backend as K
from tensorflow.keras.metrics import Mean
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
import numpy as np
import ast
import traceback
import json
import os

data_dim = 20
latent_dim = 16
epochs = 200
learning_rate = 1e-2

free_bits = 0.01
max_beta = 1.5
beta_warmup = 0.65

version = 1
dataset = "data/training_data2.txt"
models_used = ["data/car_models/Mercedes-Benz.json"]

cluster_output = "data/logs/clusters.txt"

class StochasticWeightAveragingCallback(tf.keras.callbacks.Callback):
    def __init__(self, start_epoch=100):
        super().__init__()
        self.start_epoch = start_epoch
        self.averaged_weights = None
        self.num_models = 0

    def on_epoch_end(self, epoch, logs=None):
        if epoch < self.start_epoch:
            return

        current_weights = self.model.get_weights()

        if self.averaged_weights is None:
            # Initialize with current weights
            self.averaged_weights = [np.copy(w) for w in current_weights]
        else:
            # Update simple average
            for i in range(len(self.averaged_weights)):
                self.averaged_weights[i] = (
                    self.averaged_weights[i] * self.num_models + current_weights[i]
                ) / (self.num_models + 1)

        self.num_models += 1

    def on_train_end(self, logs=None):
        if self.averaged_weights is not None:
            print(f"✅ Applying SMA weights from {self.num_models} epochs.")
            self.model.set_weights(self.averaged_weights)
        else:
            print("⚠️ No SMA applied — training ended before start_epoch.")

class KLAnnealingCallback(keras.callbacks.Callback):
    def __init__(self, vae_loss_layer, target_beta, total_epochs, start_epoch=0, warmup_epochs=50):
        super().__init__()
        self.vae_loss_layer = vae_loss_layer # Need access to the layer to modify beta
        self.target_beta = target_beta
        self.total_epochs = total_epochs
        self.start_epoch = start_epoch
        self.warmup_epochs = min(warmup_epochs, total_epochs - start_epoch)

    def on_epoch_begin(self, epoch, logs=None):
        if epoch < self.start_epoch:
            current_beta = 0.0
        elif epoch < self.start_epoch + self.warmup_epochs:
            progress = (epoch - self.start_epoch) / self.warmup_epochs
            current_beta = self.target_beta * progress
        else:
            current_beta = self.target_beta

        self.vae_loss_layer.beta.assign(current_beta)
        if epoch % 10 == 0:
           print(f"\nEpoch {epoch+1}: Setting KL beta to {current_beta:.4f}")

@tf.keras.utils.register_keras_serializable(package="Custom")
class VAELossLayer(layers.Layer):
    def __init__(self, initial_beta=1.0, **kwargs):
        super().__init__(**kwargs)
        self.beta = tf.Variable(initial_beta, trainable=False, dtype=tf.float32, name="kl_beta")

        self.recon_loss_tracker = Mean(name='recon_loss')
        self.kl_loss_tracker = Mean(name='unweighted_kl_loss')
        self.total_loss_tracker = Mean(name='total_loss')

    @property
    def metrics(self):
        return [
            self.total_loss_tracker,
            self.recon_loss_tracker,
            self.kl_loss_tracker
        ]

    def call(self, inputs):
        x, x_decoded, z_mean, z_log_var = inputs

        # reconstruction loss
        recon_loss = tf.reduce_mean(tf.square(x - x_decoded))

        # KL divergence
        kl_elementwise = -0.5 * (1 + z_log_var - K.square(z_mean) - K.exp(z_log_var))
        kl_clamped = tf.maximum(kl_elementwise, free_bits)
        kl_loss = K.mean(K.sum(kl_clamped, axis=1))

        self.total_loss_tracker.update_state(recon_loss + (self.beta * kl_loss))
        self.recon_loss_tracker.update_state(recon_loss)
        self.kl_loss_tracker.update_state(kl_loss)

        self.add_loss(recon_loss + (self.beta * kl_loss))
        return x_decoded

    def compute_output_shape(self, input_shape):
        return input_shape[0]

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
    x = layers.Dense(data_dim)(inputs)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("mish")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(128)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("mish")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(64)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("mish")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(32)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("mish")(x)
    x = layers.GaussianDropout(0.2)(x)

    z_mean = layers.Dense(latent_dim, name="z_mean")(x)
    z_log_var = layers.Dense(latent_dim, name="z_log_var")(x)
    z = Sampling()([z_mean, z_log_var])

    encoder = keras.Model(inputs, [z_mean, z_log_var, z], name="encoder")
    return encoder, z_mean, z_log_var

def decoder_architecture():
    latent_inputs = keras.Input(shape=(latent_dim,))
    x = layers.Dense(32)(latent_inputs)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("mish")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(64)(x)
    x = layers.BatchNormalization(axis=1, momentum=0.99)(x)
    x = layers.Activation("mish")(x)
    x = layers.GaussianDropout(0.2)(x)

    x = layers.Dense(128)(x)
    x = layers.Activation("mish")(x)

    x = layers.Dense(data_dim)(x)
    x = layers.Activation("softsign")(x)
    
    outputs = x

    decoder = keras.Model(latent_inputs, outputs, name="decoder")
    return decoder

def train_model():
    tf.config.list_physical_devices("GPU")

    raw_data = np.zeros((0))
    with open(dataset) as file:
        raw_data = np.array(ast.literal_eval(file.readline())) 
    train_data, val_data = train_test_split(raw_data, test_size=0.2, random_state=42)

    inputs = keras.Input(shape=(data_dim,))
    encoder, z_mean, z_log_var = encoder_architecture(inputs)
    decoder = decoder_architecture()

    # VAE Model
    decoded = decoder(encoder(inputs)[2])
    vae_loss_layer = VAELossLayer(initial_beta=0.0)
    outputs = vae_loss_layer([inputs, decoded, z_mean, z_log_var])

    vae = keras.Model(inputs, outputs, name="vae")
    vae.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate))

    sma_callback = StochasticWeightAveragingCallback(start_epoch=int(epochs * 0.5))
    kl_annealing_callback = KLAnnealingCallback(vae_loss_layer, target_beta=max_beta, total_epochs=epochs, warmup_epochs=(round(epochs * beta_warmup)))

    early_stopper = EarlyStopping(
        monitor="val_loss",
        patience=min(epochs/3, 75),
        verbose=1,
        restore_best_weights=False
    )

    lr_scheduler = ReduceLROnPlateau(
        monitor="val_loss",
        factor=0.5,
        patience=min(epochs/3, 50),
        min_lr=1e-6,
        verbose=1
    )

    vae.fit(train_data, epochs=epochs, batch_size=64, shuffle=True, validation_data=(val_data, val_data), callbacks=[sma_callback, kl_annealing_callback, early_stopper, lr_scheduler])

    os.makedirs(os.path.dirname(f"models/{version}"), exist_ok=True)
    encoder.save_weights(f"models/{version}/encoder.weights.h5", overwrite=True)
    decoder.save_weights(f"models/{version}/decoder.weights.h5", overwrite=True)
    vae.save_weights(f"models/{version}/vae.weights.h5", overwrite=True)

    vae.summary()

def load_encoder():
    # Encoder
    encoder, _, _ = encoder_architecture(keras.Input(shape=(data_dim,)))
    encoder.load_weights(f"models/{version}/encoder.weights.h5")
    return encoder

def load_decoder():
    # Decoder
    decoder = decoder_architecture()
    decoder.load_weights(f"models/{version}/decoder.weights.h5")
    return decoder

def load_vae():
    inputs = keras.Input(shape=(data_dim,))
    encoder, z_mean, z_log_var = encoder_architecture(inputs)
    decoder = decoder_architecture()

    # VAE Model
    decoded = decoder(encoder(inputs)[2])
    outputs = VAELossLayer()([inputs, decoded, z_mean, z_log_var])

    vae = keras.Model(inputs, outputs, name="vae")
    vae.load_weights(f"models/{version}/vae.weights.h5")
    return vae

def evaluate_encoder(encoder, data, labels, fig):
    z_mean, _, _ = encoder.predict(data, batch_size=64)
    labels = labels[:len(data)]

    cluster_labels = KMeans(n_clusters=round(np.sqrt(len(data)/2))).fit(z_mean).labels_

    printlist = [[] for i in range(round(np.sqrt(len(data)/2)))]
    for i in range(len(labels)):
        printlist[cluster_labels[i]].append(labels[i])
    with open(cluster_output, "w") as file:
        for i in printlist:
            file.write(f"{str(i)}\n")

    reducer = PCA(n_components=3)
    z_3d_pca = reducer.fit_transform(z_mean)

    reducer = TSNE(n_components=3, init="pca", random_state=42, perplexity=30)
    z_3d_tsne = reducer.fit_transform(z_mean)

    ax = fig.add_subplot(221, projection="3d")
    ax.scatter(z_3d_pca[:, 0], z_3d_pca[:, 1], z_3d_pca[:, 2], s=3, alpha=0.6, c=cluster_labels, cmap="tab20")
    for i, label in enumerate(labels):
        if i % 75 == 0:
            ax.text(z_3d_pca[i, 0], z_3d_pca[i, 1], z_3d_pca[i, 2], str(label), fontsize=6, alpha=0.7)
    ax.set_title(f"Latent Space Visualization (PCA)")
    ax.set_xlabel("Component 1")
    ax.set_ylabel("Component 2")
    ax.set_zlabel("Component 3")

    ax = fig.add_subplot(222, projection="3d")
    ax.scatter(z_3d_tsne[:, 0], z_3d_tsne[:, 1], z_3d_tsne[:, 2], s=3, alpha=0.6, c=cluster_labels, cmap="tab20")
    for i, label in enumerate(labels):
        if i % 75 == 0:
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
    ax.plot(range(1, len(explained_variance) + 1), np.cumsum(explained_variance), "r-o")
    ax.set_title("Explained Variance by Principal Component")
    ax.set_xlabel("Principal Component")
    ax.set_ylabel("Explained Variance Ratio")
    
    ax2 = plt.gca().twinx()
    ax2.set_ylabel("Cumulative Explained Variance")
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
    avoid = [i.strip() for i in open("data/logs/failed_dataclean.txt").readlines()]
    res = []
    for i in models_used:
        with open(i, "r") as file:
            for brand, models in json.load(file).items():
                for model in models:
                    for model_name, versions in model.items():
                        for version in versions:
                            if str([brand, model_name, version]) not in avoid:
                                res.append(" ".join([model_name, version]))
    return res

try:
    train_model()

    vae, encoder, decoder = load_model()
    raw_data = np.array(ast.literal_eval(open(dataset).readline()))
    
    fig = plt.figure(figsize=(8,8))

    evaluate_encoder(encoder, raw_data, get_trims(), fig)
    analyze_latent_dimensions(encoder, raw_data, fig)

    plt.tight_layout()
    plt.show()
except Exception:
    print(traceback.format_exc())
    while True:
        pass
