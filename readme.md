# Tabular $\beta$-VAE for Vehicle Specification Latent Modeling

An implementation of a Variational Autoencoder ($\beta$-VAE) designed to compress ~50+ multi-modal vehicle specifications into a continuous, disentangled 16-dimensional latent representation.

---

## Architecture & Optimization

* **Bottleneck:** Encodes 50+ categorical and continuous vehicle attributes into a 16-dimensional latent space ($z \in \mathbb{R}^{16}$).
* **KL Annealing:** Linearly scales the $\beta$ regularizer to prioritize initial reconstruction accuracy before regularizing toward the $\mathcal{N}(0, I)$ prior.
* **Stochastic Weight Averaging (SWA):** Implements running-weight averaging late in training to smooth gradient oscillations caused by stochastic latent sampling.

---

## Empirical Findings & Architectural Post-Mortem

Iterative experimentation and latent manifold audits revealed several critical design takeaways:

### 1. Latent Capacity & Intrinsic Dimensionality
* **Observation:** Full-rank PCA decomposition on the latent codes revealed that the top 8 components capture >90% of total variance, leaving the remaining dimensions with near-zero marginal utility.
* **Takeaway:** The physical correlations between vehicle specs (e.g., horsepower, weight, and displacement) constrain the data to an intrinsic manifold of $d \approx 8$. A 16-dimensional bottleneck leaves excess capacity, making the model prone to latent dimension collapse without explicit free-bits constraints.

### 2. Normalization & Gradient Geometry
* **Initial Approach:** Data was initially scaled to $[-1, 1]$ via naive Min-Max scaling.
* **Limitations Identified:** 
  * Right-skewed performance outliers (e.g., hypercars) heavily compressed the density of mainstream vehicles into narrow sub-intervals.
  * Uniform scaling fails to center feature distributions at zero, inducing gradient correlation across the initial dense layers.
* **Optimized Strategy:** Continuous attributes are significantly better handled via **logarithmic transforms** on heavy-tailed specs, followed by **Z-score standardization** ($\mu=0, \sigma=1$). If bounded outputs are required for the decoder, applying a zero-centered **`Softsign`** or **$\tanh$** mapping preserves linear dynamics in the primary density while smoothly dampening extreme tails.
